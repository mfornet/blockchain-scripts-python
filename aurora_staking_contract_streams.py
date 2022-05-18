from web3 import Web3
import sha3
from pprint import pprint

STREAM_SLOT = 261
RPC = 'https://mainnet.aurora.dev'
CONTRACT = '0xccc2b1aD21666A5847A804a73a41F904C4a4A0Ec'
STATUS = ['INACTIVE', 'PROPOSED', 'ACTIVE']

web3 = Web3(Web3.HTTPProvider(RPC))


def itob(value):
    return value.to_bytes(32, "big")


def btoi(value):
    return int(value.hex(), 16)


def keccak256(h):
    if isinstance(h, int):
        h = itob(h)
        r = keccak256(h)
        return btoi(r)

    k = sha3.keccak_256()
    k.update(h)
    return k.digest()


def getKey(key, mode='int'):
    value = web3.eth.get_storage_at(CONTRACT, key).hex()

    if mode == 'int':
        return int(value, 16)
    elif mode == 'address':
        return '0x' + value[-40:]
    else:
        return value


def getStream(i):
    pnt = keccak256(STREAM_SLOT)

    offset = pnt + 15 * i

    owner = getKey(offset, 'address')
    manager = getKey(offset + 1, 'address')
    rewardToken = getKey(offset + 2, 'address')
    auroraDepositAmount = getKey(offset + 3)
    auroraClaimedAmount = getKey(offset + 4)
    rewardDepositAmount = getKey(offset + 5)
    rewardClaimedAmount = getKey(offset + 6)
    maxDepositAmount = getKey(offset + 7)
    minDepositAmount = getKey(offset + 8)
    lastTimeOwnerClaimed = getKey(offset + 9)
    tau = getKey(offset + 10)
    rps = getKey(offset + 11)
    schedule_time_size = getKey(offset + 12)
    schedule_reward_size = getKey(offset + 13)
    status = getKey(offset + 14)

    schedule_time_offset = keccak256(offset + 12)
    schedule_time = [getKey(schedule_time_offset + i)
                     for i in range(schedule_time_size)]
    schedule_reward_offset = keccak256(offset + 13)
    schedule_reward = [getKey(schedule_reward_offset + i)
                       for i in range(schedule_reward_size)]

    return dict(
        owner=owner,
        manager=manager,
        rewardToken=rewardToken,
        auroraDepositAmount=auroraDepositAmount,
        auroraClaimedAmount=auroraClaimedAmount,
        rewardDepositAmount=rewardDepositAmount,
        rewardClaimedAmount=rewardClaimedAmount,
        maxDepositAmount=maxDepositAmount,
        minDepositAmount=minDepositAmount,
        lastTimeOwnerClaimed=lastTimeOwnerClaimed,
        tau=tau,
        rps=rps,
        schedule_time=schedule_time,
        schedule_reward=schedule_reward,
        status=STATUS[status]
    )


if __name__ == '__main__':

    size = getKey(STREAM_SLOT)

    print("Number of streams:", size)

    for ix in range(size):
        pprint(getStream(ix))
