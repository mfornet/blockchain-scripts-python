# a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.factory.bridge.near

import requests
import json
import pickle
import humanize
from pprint import pprint

url = "https://archival-rpc.mainnet.near.org/"
USDC = "a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.factory.bridge.near"
USDT = "dac17f958d2ee523a2206206994597c13d831ec7.factory.bridge.near"


def persist_to_file(file_name):
    def decorator(original_func):
        try:
            cache = pickle.load(open(file_name, 'rb'))
        except:
            cache = {}

        def new_func(*args, **kwargs):
            key = pickle.dumps([args, kwargs])
            if key not in cache:
                cache[key] = original_func(*args, **kwargs)
                pickle.dump(cache, open(file_name, 'wb'))
            return cache[key]

        return new_func

    return decorator


@persist_to_file('.dat/balance.pickle')
def get(token_id, block_id):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "query",
        "params": {
            "request_type": "call_function",
            "block_id": block_id,
            "account_id": token_id,
            "method_name": "ft_total_supply",
            "args_base64": "e30="
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()

    if 'error' in response and 'HANDLER_ERROR' == response['error']['name'] and 'UNKNOWN_BLOCK' == response['error']['cause']['name']:
        return get(token_id, block_id - 1)

    if 'error' in response and 'HANDLER_ERROR' == response['error']['name'] and 'UNKNOWN_ACCOUNT' == response['error']['cause']['name']:
        return 0

    try:
        return int(json.loads(bytes(response['result']['result'])))
    except:
        pprint(response)
        exit(1)


def find_blocks(token, lo, hi, supply_lo=None, supply_hi=None):
    if supply_lo is None:
        supply_lo = get(token, lo)

    if supply_hi is None:
        supply_hi = get(token, hi)

    if supply_lo == supply_hi:
        return

    if lo + 1 == hi:
        print(
            f'>> {hi} {humanize.intcomma(round(supply_lo / 1e6, 2)):>25} {humanize.intcomma(round(supply_hi / 1e6, 2)):>25} {humanize.intcomma(round((supply_hi - supply_lo) / 1e6, 0)):>25}', flush=True)

    else:
        mid = (lo + hi) // 2
        supply_mid = get(token, mid)

        find_blocks(token, mid, hi, supply_mid, supply_hi)
        find_blocks(token, lo, mid, supply_lo, supply_mid)


LO = 9820210
HI = 65852737


def main():
    find_blocks(USDT, LO, HI)


if __name__ == '__main__':
    main()
