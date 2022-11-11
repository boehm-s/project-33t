import os
import dotenv
import discogs_client
from src.discogs.album_cover_extractor import DiscogsAlbumCoverExtractor

dotenv.load_dotenv()

discogs_client = discogs_client.Client(
    'Project33T/1.0',
    user_token=os.getenv('DISCOGS_TOKEN')
)

cur_dir = os.path.dirname(os.path.realpath(__file__))
input_file = os.path.join(cur_dir, '../../ressources/discogs_20220601_releases.xml')
images_dir = os.path.join(cur_dir, '../../../images-33t')


extractor = DiscogsAlbumCoverExtractor(discogs_client, images_dir)

extractor.extract_from_xml_dump(input_file)
# extractor.extract_from_my_collection()
