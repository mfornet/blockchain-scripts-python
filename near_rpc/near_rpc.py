
import base64
from functools import lru_cache
import dotmap
import requests
import json
import utils

URL = "https://archival-rpc.mainnet.near.org/"
GENESIS_HEIGHT = 9820210


headers = {
    'Content-Type': 'application/json'
}


def rpc(paylaod):
    response = requests.request("POST", URL, headers=headers, data=paylaod)
    res = dotmap.DotMap(response.json())
    return res


@lru_cache(2**15)
@utils.memo
def block(block_id):
    return rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "block",
        "params": {"block_id": block_id}
    }))


@lru_cache(2**15)
@utils.memo
def chunk(chunk_id):
    return rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "chunk",
        "params": {"chunk_id": chunk_id}
    }))


@lru_cache(2**15)
@utils.memo
def status():
    return rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "status",
        "params": []
    }))


@lru_cache(2**15)
@utils.memo
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


@lru_cache(2**15)
@utils.memo
def EXPERIMENTAL_light_client_proof(receipt_id: str, light_client_head: str, receiver_id: str = 'aurora'):
    return rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "EXPERIMENTAL_light_client_proof",
        "params": {
            "type": "receipt",
            "receipt_id": receipt_id,
            "receiver_id": receiver_id,
            "light_client_head": light_client_head
        }
    }))


light_client_proof = EXPERIMENTAL_light_client_proof
