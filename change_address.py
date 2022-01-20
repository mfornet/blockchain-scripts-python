"""
Install web3 locally:
$> python3 -m pip install --user web3

See help with:
$> python3 change_address.py --help

To check the state of the current prover use the following command:
$> python3 change_address.py --rpc <RPC_ENDPOINT> --prover 0xb3df48b0ea3e91b43226fb3c5eb335b7e3d76faa

To update the bridge address of the prover use the following command:
$> python3 change_address.py --rpc <RPC_ENDPOINT> --prover 0xb3df48b0ea3e91b43226fb3c5eb335b7e3d76faa --sk ropsten_admin.txt --bridge 0xb289c6e6c98644dc9f6a03c044564bc8558b6087 --change

(1) Notice that in this case ropsten_admin.txt is a file that contains the secret key. It will look for the first secret key on that file and use it.

(2) It is required that NearProver.full.abi is available at the same location where the script is located, otherwise, pass the path to the abi file using --abi. Get the abi from: https://github.com/near/rainbow-bridge/blob/master/contracts/eth/nearprover/dist/NearProver.full.abi
"""
import argparse
import json
import re
from pathlib import Path

from web3 import Web3


MASK = 0xffffffffffffffffffffffffffffffffffffffff
BRIDGE_ADMIN_POSITION = 0
PAUSED_POSITION = 1
BRIDGE_ADDRESS_POSITION = 2


def read_storage(web3, prover_address, abi):
    prover = web3.eth.contract(address=prover_address, abi=abi)

    admin_address = prover.functions.admin().call()
    raw_admin_address = web3.eth.get_storage_at(
        prover_address, BRIDGE_ADMIN_POSITION).hex()
    assert int(admin_address, 16) == int(raw_admin_address,
                                         16), f"{admin_address} {raw_admin_address}"

    paused = prover.functions.paused().call()
    raw_paused = web3.eth.get_storage_at(prover_address, PAUSED_POSITION).hex()
    assert paused == int(raw_paused, 16), f"{paused} {raw_paused}"

    bridge_address = prover.functions.bridge().call()
    raw_bridge_address = web3.eth.get_storage_at(prover_address, 2).hex()
    assert int(bridge_address, 16) == int(raw_bridge_address,
                                          16), f"{bridge_address} {raw_bridge_address}"

    print("\nStorage View")
    print("Contract:", prover_address)
    print("Admin address:", admin_address)
    print("Paused:", paused)
    print("Bridge address:", bridge_address)
    print()


def set_storage(web3, prover_address, bridge, abi, admin_account):
    assert web3.isAddress(bridge), bridge
    nonce = web3.eth.get_transaction_count(admin_account.address)
    prover = web3.eth.contract(address=prover_address, abi=abi)

    raw_tx = prover.functions.adminSstoreWithMask(
        2, int(bridge, 16), MASK).buildTransaction({"from": admin_account.address, "nonce": nonce})

    signed_tx = web3.eth.account.signTransaction(
        raw_tx, admin_account.privateKey)

    web3.eth.send_raw_transaction(*signed_tx)


def load_abi(abi_path):
    with open(abi_path) as f:
        return json.load(f)


def load_sk(path):
    try:
        with open(path) as f:
            data = f.read()
            result = re.search('0x[0-9a-fA-F]{64}', data)
            return result.group(0)
    except Exception as e:
        print("Error: Path not found or secret key not found.")
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Change prover address", usage=__doc__)

    parser.add_argument('--rpc', required=True, help="Endpoint RPC.")
    parser.add_argument('--prover', required=True, help="Prover address.")
    parser.add_argument('--sk', help="File storing admin secret key.")
    parser.add_argument('--abi', help="Path to the contract abi.")
    parser.add_argument('--bridge', help="New bridge address", default='')
    parser.add_argument('--change', action='store_true', default=False,
                        help="Check current status of the prover without changing the address")

    args = parser.parse_args()

    print("Using args:", args)

    web3 = Web3(Web3.HTTPProvider(args.rpc))
    print("Network block number:", web3.eth.blockNumber)

    if args.abi is None:
        if not Path('NearProver.full.abi').exists():
            print("Error: Provide path to NearProver.full.abi with --abi")
            exit(1)
        else:
            args.abi = str(Path('NearProver.full.abi').absolute())

    args.prover = Web3.toChecksumAddress(args.prover)

    abi = load_abi(args.abi)
    read_storage(web3, prover_address=args.prover, abi=abi)

    if not args.change:
        print(
            "Running in dry mode. To change the bridge address pass the flag --change")
    else:
        if args.sk is None:
            print(
                "Error: Specify the path where the admin secret key is stored with --sk <path>")
            exit(1)

        admin_sk = load_sk(args.sk)
        admin_account = web3.eth.account.privateKeyToAccount(admin_sk)

        print("Admin address:", admin_account.address)

        set_storage(web3, prover_address=args.prover, bridge=args.bridge,
                    abi=abi, admin_account=admin_account)
        read_storage(web3, prover_address=args.prover, abi=abi)
