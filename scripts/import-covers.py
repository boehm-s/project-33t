import os
import glob
import dotenv
import discogs_client
import xml.etree.ElementTree as etree
import pathlib
import urllib
import time


dotenv.load_dotenv()

d = discogs_client.Client(
    'Project33T/1.0',
    user_token=os.getenv('DISCOGS_TOKEN')
)

cur_dir = os.path.dirname(os.path.realpath(__file__))
source = os.path.join(cur_dir, '../ressources/discogs_20220601_releases.xml')

def already_saved_cover(release_id: str, master_id: str) -> bool:
    master_dir = os.path.join(cur_dir, '../images/', master_id)
    if not os.path.exists(master_dir):
        return False
    filematches = glob.glob(os.path.join(master_dir, "{}_front_cover.*".format(release_id)))
    return len(filematches) > 0

start_time = time.time()
for event, elem in etree.iterparse(source, events=("start",)):
    if elem.tag == "release":
        formats = elem.find('formats')
        is_vinyl_release = formats is not None and any(f.get('name') == 'Vinyl' for f in formats)
        master = elem.find('master_id')

        if is_vinyl_release and master is not None:
            release_id = elem.get('id')
            master_id = master.text
            if master_id is None:
                print("No master for release {}".format(release_id))
                continue
            if already_saved_cover(release_id, master_id):
                print("Already saved cover for album {}/{}".format(master_id, release_id))
                continue
            release = d.release(release_id)
            if release.images is None:
                print("No images for album {}/{}".format(master_id, release_id))
                continue
            front_cover = next(filter(lambda x: x.get('type') == 'primary', release.images), None)
            if front_cover is None:
                continue
            front_cover_uri = front_cover.get('uri')
            filename, file_extension = os.path.splitext(front_cover_uri)
            filedir = os.path.join(cur_dir, '../images/', master_id)
            pathlib.Path(filedir).mkdir(parents=True, exist_ok=True)

            filename = "{}_front_cover{}".format(release_id, file_extension)
            filepath = os.path.join(filedir, filename)
            if os.path.exists(filepath):
                continue
            end_time = time.time()
            ellapsed_time = end_time - start_time
            sleep_time = max((1.02 - ellapsed_time), 0)
            time.sleep(sleep_time)
            urllib.request.urlretrieve(front_cover_uri, filepath)
            start_time = time.time()
            time_between_requests = ellapsed_time + sleep_time
            print(filepath)

        elem.clear()
