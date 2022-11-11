import glob
import json
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
        """Init DiscogsAlbumCoverIndexer with."""
        self.discogs_client = discogs_client
        self.images_dir = images_dir
        self.rate_limiter = RateLimiter(0.98)

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
        images_files = glob.glob("{}/*_*".format(self.images_dir))
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
