import os
import glob
import sys
import dotenv
import discogs_client
import requests
import json

cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(cur_dir, '../src/'))

def build_metadata(filename: str):
    """Build metadata for discogs image given its filename."""
    parts = filename.split('_')
    discogs_release_id = parts[0]
    discogs_master_id = parts[1]
    discogs_release = discogs_client.release(discogs_release_id)
    discogs_release.fetch('data')
    return json.dumps({
        "discogs_release_id": discogs_release_id,
        "discogs_master_id": discogs_master_id,
        "discogs_release_data": discogs_release.data
    })


dotenv.load_dotenv()

discogs_client = discogs_client.Client(
    'Project33T/1.0',
    user_token=os.getenv('DISCOGS_TOKEN')
)

i = 0
images_dir = os.path.join(cur_dir, '../images/')
images_files = glob.glob("{}*_*".format(images_dir))
for filepath in images_files:
    filename = filepath.split('/')[-1]
    metadata = build_metadata(filename)
    elastic_filepath = f"discogs/{filename}"
    files = {'image': open(filepath, 'rb')}
    values = {'filepath': elastic_filepath}
    r = requests.post('http://localhost:8888/add', files=files, data=values)
    status = r.json().get('status')
    print("{} : {}".format(filename, status))
    if i > 10:
        break
    i = i + 1
