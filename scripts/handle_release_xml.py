import json
import os
import sys
import xml.etree.ElementTree as etree
import urllib
import time
from typing import List


class DiscogsReleasesXMLParser:
    """TODO."""

    def __init__(self, discogs_client, input_file, images_dir):
        """TODO."""
        self.discogs_client = discogs_client
        self.input_file = input_file
        self.images_dir = images_dir

    def list_saved_release_id(self) -> List[int]:
        """TODO."""
        saved_releases = []
        for path, subdirs, files in os.walk(self.images_dir):
            for name in [f for f in files if "primary" in f]:
                release_id = int(name.split("_")[0])
                saved_releases.append(release_id)

        saved_releases.sort()
        return saved_releases

    def get_latest_saved_release_id(self) -> int:
        """TODO."""
        saved_release_ids = self.list_saved_release_id()
        return saved_release_ids[-1]

    def parse(self):
        """TODO."""
        start_time = time.time()
        latest_saved_release_id = self.get_latest_saved_release_id()
        for event, elem in etree.iterparse(self.input_file, events=("start",)):
            if elem.tag == "release":
                formats = elem.find('formats')
                is_vinyl_release = formats is not None and any(f.get('name') == 'Vinyl' for f in formats)
                master = elem.find('master_id')

                if is_vinyl_release and master is not None:
                    release_id = elem.get('id')
                    if int(release_id) <= latest_saved_release_id:
                        print("Already parsed release {}".format(release_id))
                        elem.clear()
                        continue
                    master_id = master.text

                    try:
                        front_cover_url = get_front_cover_url(self.discogs_client, elem)
                    except AlbumCoverURLNotFound as err:
                        print(err, file=sys.stderr)
                        elem.clear()
                        continue

                    filename, file_extension = os.path.splitext(front_cover_url)
                    filename = "{}_{}_primary{}".format(release_id, master_id, file_extension)
                    filepath = os.path.join(self.images_dir, filename)
                    if os.path.exists(filepath):
                        elem.clear()
                        continue
                    end_time = time.time()
                    ellapsed_time = end_time - start_time
                    sleep_time = max((1.02 - ellapsed_time), 0)
                    time.sleep(sleep_time)
                    try:
                        urllib.request.urlretrieve(front_cover_url, filepath)
                    except:
                        print(
                            "Downloading cover failed for release {} ({})"
                            .format(release_id, front_cover_url)
                        )
                    start_time = time.time()
                    print(filepath)

            elem.clear()


class AlbumCoverURLNotFound(Exception):
    """Raise when we cannot find an album's cover."""

    pass


def get_front_cover_url(discogs_client, xml_release) -> str:
    """Return the given release's front cover URL.

    Args:
        discogs_client: an authenticated instance of discogs_client
        xml_release: a <release> ElementTree from a discogs release dump

    Returns:
        str: The URL of the album relase front cover.

    Raises:
        AlbumCoverURLNotFound: The front cover URL could not been found.
    """
    release_id = xml_release.get('id')
    xml_master = xml_release.find('master_id')
    if xml_master is None or xml_master.text is None:
        raise AlbumCoverURLNotFound(
            "Could not find master_id associated with release {}"
            .format(release_id)
        )
    try:
        release = discogs_client.release(release_id)
    except json.decoder.JSONDecodeError:
        raise AlbumCoverURLNotFound(
            "Decoding release {} failed".format(release_id)
        )
    except:
        raise AlbumCoverURLNotFound(
            "Discogs client failed fetching release {}".format(release_id)
        )
    if release.images is None:
        raise AlbumCoverURLNotFound(
            "No images for release {}".format(release_id)
        )
    front_cover = next(
        filter(lambda x: x.get('type') == 'primary', release.images),
        None
    )
    if front_cover is None:
        raise AlbumCoverURLNotFound(
            "No front cover for release {}".format(release_id)
        )

    return front_cover.get('uri')
