import os
from typing import List

def list_saved_release_id() -> List[int]:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    images_dir = os.path.join(current_dir, '../images')
    saved_releases = []
    for path, subdirs, files in os.walk(images_dir):
        for name in files:
            release_id = int(name.split("_")[0])
            saved_releases.append(release_id)

    saved_releases.sort()
    return saved_releases

def get_latest_saved_release_id() -> int:
    saved_release_ids = list_saved_release_id()
    return saved_release_ids[-1]

print(get_latest_saved_release_id())
