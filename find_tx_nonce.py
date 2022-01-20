"""
Find a transaction where the nonce increased on Aurora
"""
import base64
import dotmap
import requests
import json

URL = "https://archival-rpc.mainnet.near.org/"
GENESIS_HEIGHT = 9820210


def normalize(address: str):
    if address.startswith('0x'):
        address = address[2:]
    return bytes.fromhex(address)


headers = {
    'Content-Type': 'application/json'
}


def rpc(paylaod):
    response = requests.request("POST", URL, headers=headers, data=paylaod)
    res = dotmap.DotMap(response.json())
    return res


def status():
    return rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "status",
        "params": []
    }))


def call_function(account_id: str, method: str, args: bytes, block_id: int):
    return rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "query",
        "params": {
            "request_type": "call_function",
            "block_id": block_id,
            "account_id": account_id,
            "method_name": method,
            "args_base64": base64.b64encode(args).decode()
        }
    }))


def get_nonce(address: str, block_id: int):
    address = normalize(address)
    res = call_function('aurora', 'get_nonce', address, block_id)
    if 'error' in res:
        return 0
    return res.result.result[-1]


def find_blocks_for_txs(address: str):
    lo = GENESIS_HEIGHT
    hi = status().result.sync_info.latest_block_height

    nonce_lo = get_nonce(address, lo)
    nonce_hi = get_nonce(address, hi)

    print(lo, nonce_lo)
    print(hi, nonce_hi)

    if nonce_hi == nonce_lo:
        pass

    heights = []

    def search(lo, nonce_lo, hi, nonce_hi):
        if nonce_lo == nonce_hi:
            return

        if lo + 1 == hi:
            heights.append(hi)
            return

        mid = (lo + hi) // 2
        nonce_m = get_nonce(address, mid)

        search(lo, nonce_lo, mid, nonce_m)
        search(mid, nonce_m, hi, nonce_hi)

    search(lo, nonce_lo, hi, nonce_hi)
    return heights


def main():
    address = '0x23b519fb0fb0a216db87bfe3c6a5d2a1e07b2ebe'
    H = find_blocks_for_txs(address)
    print(H)


if __name__ == '__main__':
    main()
