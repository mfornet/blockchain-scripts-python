from web3 import Web3
from utils import infura_provider_url


def check_slots(address: str, num_slots=10):
    web3 = Web3(Web3.HTTPProvider(infura_provider_url()))
    for position in range(num_slots):
        value = web3.eth.get_storage_at(address, position).hex()
        print(position, value)


if __name__ == '__main__':
    check_slots('0x85F17Cf997934a597031b2E18a9aB6ebD4B9f6a4')
