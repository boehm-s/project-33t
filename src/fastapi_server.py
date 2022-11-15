from typing import Optional

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from os import environ
import json

from .image_match.elasticsearch_driver import SignatureES
from .image_match.goldberg import ImageSignature

load_dotenv()

es_url = environ['ELASTICSEARCH_URL']
es_index = environ['ELASTICSEARCH_INDEX']
es_doc_type = environ['ELASTICSEARCH_DOC_TYPE']
all_orientations = environ['ALL_ORIENTATIONS']

es = Elasticsearch(es_url)
ses = SignatureES(es, index=es_index, doc_type=es_doc_type)
gis = ImageSignature()

# Try to create the index and ignore IndexAlreadyExistsException
# if the index already exists
es.indices.create(index=es_index, ignore=400)

app = FastAPI()

@app.get("/add")
def add_handler(
        image: Optional[UploadFile] = File(),
        path: Optional[str] = Form(),
        metadata: str = Form(),
):
    try:
        metadata = json.loads(metadata)
    except KeyError:
        metadata = None

    if image:
        bs = True
        img = image.file
    elif path:
        bs = False
        img = path
    else:
        raise HTTPException(status_code=400, detail="You must specify a path or an image")

    # First, delete the old matches, to upsert the image
    old_matches = es.search(index=es_index, _source='_id', q='path:' + json.dumps(path))
    for m in old_matches['hits']['hits']:
        es.delete(index=es_index, doc_type=es_doc_type, id=m['_id'], ignore=404)

    # Then, add the current image
    ses.add_image(path, img, bytestream=bs, metadata=metadata)

    return json.dumps({
        'status': 'ok',
    })

@app.get("/count")
async def count_handler():
    count = es.count(index=es_index)['count']
    return json.dumps({
        'count': count,
    })
