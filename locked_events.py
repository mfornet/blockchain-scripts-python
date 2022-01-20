"""
Get locked events from Locker contract in ethereum (using etherscan API)
"""

from web3 import Web3
from utils import infura_provider_url, persist_to_file
from dotmap import DotMap
import requests
from rlp import decode
from sha3 import keccak_256
import os
import utils

LOCKER_ADRESS = '0x23ddd3e3692d1861ed57ede224608875809e127f'
URL_TEMPLATE = f"https://api.etherscan.io/api?module=account&action=txlist&address={LOCKER_ADRESS}&startblock=0&endblock=<HEIGHT>&sort=asc&apikey={os.environ['ETHERSCAN_API_KEY']}"
LOCKED_EVENT_ID = '0x' + keccak_256(
    b'Locked(address,address,uint256,string)').hexdigest()


def decode_log(log):
    token_address = '0x' + log.topics[1].hex()[-40:]
    sender = '0x' + log.topics[2].hex()[-40:]
    amount = int(log.data[2:2+64], 16)
    target = bytes.fromhex(log.data[-64:]).strip(b'\x00').decode()

    return dict(
        token=token_address,
        sender=sender,
        amount=amount,
        target=target,
    )


def main():
    w3 = Web3(Web3.HTTPProvider(infura_provider_url()))

    @persist_to_file('.dat/locker_events')
    def get_events():
        block_number = w3.eth.block_number
        url = URL_TEMPLATE.replace('<HEIGHT>', str(block_number))
        return requests.get(url).json()

    @persist_to_file('.dat/receipts')
    def get_receipt(tx_hash):
        return w3.eth.get_transaction_receipt(tx_hash)

    events = DotMap(get_events())
    print("Number of transactions:", len(events.result))

    for _ix, tx in enumerate(events.result):
        receipt = get_receipt(tx.hash)
        for log in receipt.logs:
            if log.topics[0].hex() == LOCKED_EVENT_ID:
                print(tx.hash)
                info = decode_log(log)
                info['txHash'] = tx.hash
                from pprint import pprint
                pprint(info)


if __name__ == '__main__':
    main()
