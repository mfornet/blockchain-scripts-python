import os

from dotenv import load_dotenv
from requests import get
from near_rpc.utils import persist_to_file

load_dotenv()

INFURA_API_KEY = os.environ.get('INFURA_API_KEY')


def infura_provider_url(target_network='mainnet'):
    return f'https://{target_network}.infura.io/v3/{INFURA_API_KEY}'


@persist_to_file('.dat/scripts')
def get_file(url):
    return get(url).content.decode()
