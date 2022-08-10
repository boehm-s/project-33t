import os
import dotenv
import discogs_client
from handle_release_xml import DiscogsReleasesXMLParser

dotenv.load_dotenv()

discogs_client = discogs_client.Client(
    'Project33T/1.0',
    user_token=os.getenv('DISCOGS_TOKEN')
)

cur_dir = os.path.dirname(os.path.realpath(__file__))
input_file = os.path.join(cur_dir, '../ressources/discogs_20220601_releases.xml')
images_dir = os.path.join(cur_dir, '../images/')


parser = DiscogsReleasesXMLParser(discogs_client, input_file, images_dir)

parser.parse()
