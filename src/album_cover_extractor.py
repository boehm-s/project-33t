import os
import glob
import sys
import xml.etree.ElementTree as etree
import urllib
import time
from typing import List, Tuple


class DiscogsAlbumCoverExtractor:
    """Parser for Discogs release dump files."""

    def __init__(self, discogs_client, images_dir):
        """Init DiscogsReleasesXMLParser with."""
        self.discogs_client = discogs_client
        self.images_dir = images_dir
        self.start_time = time.time()

    def list_saved_release_id(self) -> List[int]:
        """Return a list of all saved releases ID."""
        saved_releases = []
        for _path, _subdirs, files in os.walk(self.images_dir):
            for name in [f for f in files if "primary" in f]:
                release_id = int(name.split("_")[0])
                saved_releases.append(release_id)

        saved_releases.sort()
        return saved_releases

    def get_latest_saved_release_id(self) -> int:
        """Return the latest saved release ID."""
        saved_release_ids = self.list_saved_release_id()
        return saved_release_ids[-1]

    def release_already_saved(self, release_id: int) -> bool:
        """Return true if we've already saved the relase and false otherwise.

        Args:
            release_id (int): the Realease ID
        """
        matches = glob.glob(f"{self.images_dir}{release_id}_*")

        return len(matches) > 0

    def reset_rate_limit_timer(self):
        """Reset the rate limiting timer."""
        self.start_time = time.time()

    def wait_for_rate_limit(self):
        """Wait 1 second after last image request to Discogs."""
        end_time = time.time()
        ellapsed_time = end_time - self.start_time
        sleep_time = max((1.02 - ellapsed_time), 0)
        time.sleep(sleep_time)

    def download_cover(self, master_id, release_id, cover_url) -> str:
        """Download the given release's cover image and wait for rate limiting.

        Args:
            master_id (int): The Master ID of the release
            release_id (int): The Release ID.
            cover_url (str): The URL of the release's front cover
        Returns:
            str: The file path of the downloaded cover.

        Raises:
            DownloadCoverFailed: The cover could not be downloaded.
        """
        filename, ext = os.path.splitext(cover_url)
        filename = f"{release_id}_{master_id}_primary{ext}"
        filepath = os.path.join(self.images_dir, filename)
        self.wait_for_rate_limit()
        try:
            urllib.request.urlretrieve(cover_url, filepath)
        except Exception as err:
            raise DownloadCoverFailed(
                f"Download cover failed for release {release_id} ({cover_url})"
            ) from err
        self.reset_rate_limit_timer()

        return filepath

    def extract_from_my_collection(self):
        """Extract the album covers from my discogs collection."""
        me = self.discogs_client.identity()
        for item in me.collection_folders[0].releases:
            release_id = item.release.id
            if self.release_already_saved(release_id):
                continue
            try:
                release = self.discogs_client.release(release_id)
                master_id = release.master.id
                front_cover_url = get_front_cover_url(release)
                filepath = self.download_cover(
                    master_id,
                    release_id,
                    front_cover_url
                )
            except Exception as err:
                print(err, file=sys.stderr)
                continue

            print(filepath)

    def extract_from_xml_dump(self, input_file):
        """Extract the album covers."""
        latest_saved_release_id = self.get_latest_saved_release_id()

        for _event, elem in etree.iterparse(input_file, events=("start",)):
            if elem.tag == "release":
                try:
                    master_id, release_id = validate_xml_release(
                        elem,
                        latest_saved_release_id
                    )
                    if self.release_already_saved(release_id):
                        continue
                    release = self.discogs_client.release(release_id)
                    front_cover_url = get_front_cover_url(release)
                    filepath = self.download_cover(
                        master_id,
                        release_id,
                        front_cover_url
                    )
                except Exception as err:
                    print(err, file=sys.stderr)
                    elem.clear()
                    continue

                print(filepath)

            elem.clear()


class DownloadCoverFailed(Exception):
    """Raise when we the download of a cover falied."""


class AlbumCoverURLNotFound(Exception):
    """Raise when we cannot find an album's cover."""


class UnprocessableRelease(Exception):
    """Raise when a release is considered unprocessable.

    For example: an album without vinyl release,
    or without valid master_id and release_id
    """


def validate_xml_release(xml_release, last_release_id=None) -> Tuple[int, int]:
    """Return the given release's master_id and release_id.

    Args:
        xml_release (:obj): a <release> ElementTree from a discogs release dump
        last_release_id (int, optional): the latest saved release_id. Defaults
            to None. If given, all inferior releases will be considered treated
            and thus "Unprocessable".

    Returns:
        int: The master_id of the release
        int: The release_id.

    Raises:
        UnprocessableRelease: The release cannot be processed.
    """
    release_id = xml_release.get('id')
    if release_id is None:
        raise UnprocessableRelease("Could not determine release_id ")
    release_id = int(release_id)

    if (last_release_id is not None and release_id <= last_release_id):
        raise UnprocessableRelease(f"Already parsed release {release_id}")

    formats = xml_release.find('formats')
    if formats is None:
        raise UnprocessableRelease(
            f"No format associated with release {release_id}"
        )

    is_vinyl_release = any(f.get('name') == 'Vinyl' for f in formats)
    if not is_vinyl_release:
        raise UnprocessableRelease(
            f"No vinyl associated with release {release_id}"
        )

    master = xml_release.find('master_id')
    if master is None or master.text is None:
        raise UnprocessableRelease(
            f"Could not find master_id for release {release_id}"
        )
    master_id = int(master.text)

    return master_id, release_id


def get_front_cover_url(release) -> str:
    """Return the given release's front cover URL.

    Args:
        release (:obj): a "Release" from the discogs_client

    Returns:
        str: The URL of the album relase front cover.

    Raises:
        AlbumCoverURLNotFound: The front cover URL could not been found.
    """
    if release.images is None:
        raise AlbumCoverURLNotFound(f"No images for release {release.id}")
    front_cover = next(
        filter(lambda x: x.get('type') == 'primary', release.images),
        None
    )
    if front_cover is None:
        raise AlbumCoverURLNotFound(f"No front cover for release {release.id}")

    return front_cover.get('uri')
