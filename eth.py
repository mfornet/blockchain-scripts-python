"""
Compute address from private key.
"""

from coincurve import PublicKey
from sha3 import keccak_256


def remove_prefix(value):
    if value.startswith('0x'):
        value = value[2:]
    return value


rp = remove_prefix

private_key = bytes.fromhex(rp(input("Input private key: ")))
public_key = PublicKey.from_valid_secret(
    private_key).format(compressed=False)[1:]
addr = keccak_256(public_key).digest()[-20:]
print('private_key:', private_key.hex())
print('eth addr: 0x' + addr.hex())
