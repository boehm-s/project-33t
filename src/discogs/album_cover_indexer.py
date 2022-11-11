import glob
import json
import os.path

import requests
import sys

from src.discogs.rate_limiter import RateLimiter


class DiscogsAlbumCoverIndexer:
    """Indexer for Discogs cover images.

    This class contains methods that allow us to take the images extracted
    by the DiscogsAlbumCoverExtractor, fetch additional data and index the
    resulting data (elaticsearch).
    """

    def __init__(self, discogs_client, images_dir):
        """Init DiscogsAlbumCoverIndexer with discogs_client and images_dir."""
        self.discogs_client = discogs_client
        self.images_dir = images_dir
        self.rate_limiter = RateLimiter(0.98)

    def list_indexed_files(self) -> list[str]:
        """List the discogs files already indexed in ES"""
        try:
            r = requests.get('http://localhost:8888/list-discogs-files')
            result = r.json()
        except Exception as err:
            print(err, file=sys.stderr)
            raise ListIndexedDiscogsFilesFailed() from err

        return result["result"]

    def list_files_to_process(self) -> list[str]:
        print("Listing already indexed discogs files ...")
        indexed_files = self.list_indexed_files()
        images_files = glob.glob(f"{self.images_dir}/*_*")
        print("Listing files to process ...")
        for filename in indexed_files:
            image_file_to_skip = f"{self.images_dir}/{filename}"
            try:
                images_files.remove(image_file_to_skip)
            except Exception:
                print(f"Indexed file not found in file list : {filename}")

        print("Ready to process files ...")
        return images_files

    def build_metadata(self, filename: str) -> str:
        """Build metadata for discogs image given its filename."""
        [discogs_release_id, discogs_master_id, _] = filename.split('_')
        self.rate_limiter.wait_for_rate_limit()
        try:
            discogs_release = self.discogs_client.release(discogs_release_id)
            discogs_release.fetch('data')
        except Exception as err:
            raise DownloadMetadataFailed(
                f"Download metadata failed for release {discogs_release_id}"
            ) from err
        self.rate_limiter.reset_timer()

        return json.dumps({
            "discogs_release_id": discogs_release_id,
            "discogs_master_id": discogs_master_id,
            "discogs_release_data": discogs_release.data
        })

    def index(self):
        images_files = self.list_files_to_process()
        for filepath in images_files:
            filename = filepath.split('/')[-1]
            try:
                metadata = self.build_metadata(filename)
            except Exception as err:
                metadata = json.dumps({"error": 'no.metadata'})
                print(err, file=sys.stderr)

            elastic_filepath = f"discogs/{filename}"
            values = {'filepath': elastic_filepath, 'metadata': metadata}
            try:
                files = {'image': open(filepath, 'rb')}
                r = requests.post('http://localhost:8888/add', files=files, data=values)
                status = r.json().get('status')
                print("{} : {}".format(filename, status))
            except Exception as err:
                print(err, file=sys.stderr)


class DownloadMetadataFailed(Exception):
    """Raise when we failed to fetch metadata for the release."""

class ListIndexedDiscogsFilesFailed(Exception):
    """Raise when we fail to list the already indexed discogs files."""
