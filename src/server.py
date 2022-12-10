from typing import Optional

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from os import environ
import json
import time

from src.image_match.elasticsearch_driver import SignatureES
from src.image_match.goldberg import ImageSignature

load_dotenv()

ES_URL = environ['ELASTICSEARCH_URL']
ES_INDEX = environ['ELASTICSEARCH_INDEX']
ES_DOC_TYPE = environ['ELASTICSEARCH_DOC_TYPE']
ALL_ORIENTATIONS = environ['ALL_ORIENTATIONS']

es = Elasticsearch(ES_URL)
ses = SignatureES(es, index=ES_INDEX, doc_type=ES_DOC_TYPE)
gis = ImageSignature()

# Try to create the index and ignore IndexAlreadyExistsException
# if the index already exists
es.indices.create(index=ES_INDEX, ignore=400)

app = FastAPI()


def get_image(url_field: Optional[str], file_field: Optional[bytes]):
    if url_field is not None and file_field is not None:
        raise HTTPException(status_code=400, detail="You cannot provide an image and an URL, you must chose one")

    if url_field:
        return url_field, False
    elif file_field:
        return file_field, True
    else:
        raise HTTPException(status_code=400, detail="You must provide an image as a file or an URL")


@app.post("/add")
def add_handler(
        image: Optional[bytes] = File(),
        url: Optional[str] = Form(None),
        filepath: Optional[str] = Form(),
        metadata: str = Form(),
):
    try:
        metadata = json.loads(metadata)
    except KeyError:
        metadata = None

    img, bs = get_image(url, image)
    # First, delete the old matches, to upsert the image
    old_matches = es.search(index=ES_INDEX, _source='_id', q='path:' + json.dumps(filepath))
    for m in old_matches['hits']['hits']:
        es.delete(index=ES_INDEX, doc_type=ES_DOC_TYPE, id=m['_id'], ignore=404)

    # Then, add the current image
    ses.add_image(filepath, img, bytestream=bs, metadata=metadata)

    return JSONResponse(content={
        'status': 'ok',
    })


@app.post("/search")
async def search_handler(
        image: Optional[bytes] = File(None),
        url: Optional[str] = Form(None),
        all_orientations: bool = Form(),
):
    img, bs = get_image(url, image)

    start_time = time.time()
    matches = ses.search_image(
        path=img,
        all_orientations=all_orientations or ALL_ORIENTATIONS,
        bytestream=bs)
    end_time = time.time()
    search_time = end_time - start_time

    return JSONResponse(content={
        'status': 'ok',
        'search_time': search_time,
        'result': [{
            'score': (1 - m['dist']) * 100,
            'filepath': m['path'],
            'metadata': m['metadata']
        } for m in matches]
    })

@app.get("/list-discogs-files")
async def list_discogs_files_handler():
    result = []
    query = {
        "_source": "images.path",
        "query": {"match_all": {}}
    }

    for hit in scan(es, index=ES_INDEX, query=query):
        path = hit["_source"]["images"]["path"]
        filename = path.split("/")[1]
        result.append(filename)

    return JSONResponse(content={
        'result': result
    })

@app.get("/count")
async def count_handler():
    count = es.count(index=ES_INDEX)['count']
    return JSONResponse(content={
        'count': count
    })
