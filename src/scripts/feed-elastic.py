import os
import dotenv
import discogs_client

from src.discogs.album_cover_indexer import DiscogsAlbumCoverIndexer

dotenv.load_dotenv()

cur_dir = os.path.dirname(os.path.realpath(__file__))
discogs_client = discogs_client.Client(
    'Project33T/1.0',
    user_token=os.getenv('DISCOGS_TOKEN')
)
images_dir = os.path.join(cur_dir, '../../../images-33t')
print(images_dir)
indexer = DiscogsAlbumCoverIndexer(discogs_client, images_dir)
indexer.index()
