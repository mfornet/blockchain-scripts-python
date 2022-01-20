from abc import abstractmethod
import struct
from typing import List, Optional, TypeVar, Type, Union
import hashlib


BLOCK_PROOF = '05000000febda3871650957495eb72e4cf53b02ec9a5a7d792d723e80ed2ddfd7b734ef400981e4f19fa0928763d7708169d49b3fe5db6ba02f38b0528f0c7c7fb8f353e1801d14a2b3cba19860d3d0a52ff8f75ce318fc6b26a143ab25f4daa2d715e7ab4d3019849669f0f03ea2d3e90ab94519b256107a667ca32791274f062562bb266b72d01347004af573e4f12ef703f36cbfbb0f808a7ee559bca5d48ea60cb9c4049151d011a3662805ec05aec9c17c246ead6c0a45f5e85fe7e5b8a69ea16dccc7683cf423629b7f9db12f5dcca8f033ac2943fd21371492265043ee19e7672aa73386e71000000000100000099da04a0e93a1dfba23957b7ed39f28f0e1ec91bf0def78459bd0e8622dfbd715177c1cf0a040000003163cf141cf5171800000000000000060000006175726f726102380000001bea651b6be9562a0000000000000000779d00d9851a2a0d7e3bdf10dc6577a27fd46a756bfad42cfc4efc96f529d786d643ff4a8b89fa520200000035dae86a386b72e30a8c6c632583a398a3aba3b9981b37240e89e6a4144fed4600117a1f85788d83b5434f01cec2b47cf9ba7970f189a960635a94b655bc2f488b01bcc8573c58ddad3461b0b39a581d7823851dd49d0d142f042b27d6b015b7aa6a1fbfad53cb0dbdb22cd090d402bffbd9521db5bb6cccb858dbaa75261b8d6ea4e30f6e03000000003910b09ccae28d1cb1ad5e0de92ec4f04bab63d5edc133857e162c424392830d35c8a3b2adad97c010448669b20efb6e02e3ae432b645c015c819075130e472deed644ad6100200ff4c323dedb3cf1fd48e4b9b8255b9ee1ac48d150c33e92b134ae2535c0fce4ee55d6de75dfc922fd33b671f479a1c4284c20716365d060bc8e6989a4b9e2ca167bc65d3df4a4f2acd5098781f95daaa947ed9f04fcb4027ce8e4c7e10ac75410add56701cac6e7cc3c7cf52da0b85af524ec150722e07b455299312c54547ba01800000016b630da92d7f9658db081bb9d1c23a22f98cfca5362dba6e06d7e304ca029f4011e443d1b804d2eb85624062d0443cee821083df302de6f84a85824f76f316b4601d1bab587f86a04f734c4419c1dab1733dd62acb96a68c5344cdd76dc02e584340068a5d986d351d85ea722a40223a969300a734a63187987f7d70c571c8cd45736014b1dbd274fc7f942a077ec21e85cf1495bd63f830fc28a468c73fc3647f266ff008242d70cb42363fa57b9287d3f1295a89615a7b46bde8bd54d205dbfd4130e1b00eaea18c3df9a08c893d178589d5a02a00d192b2fe6d2efdf1e9ac3d743a899ae00ade4e7b05bbad81e51bd18ec6567e979e02d72216ab8963bd6a0109fe2d8444100442832b1d8f797cd7533eda7a857a4d63ef7db89239cafd19cee5ba4254bc70d01990a0cc36e03ff4cfab6da47df2ee1338976a0fe5579caa0c80702219bb93a3001f064aed3026ad47d8402f7db1dc49caee2bf9032481cd7579f406c988eeae042007ea638d41d6de621a60b8bf5195f0361d80d660a8a42957e19e296bd0b34667d009011917395515a7ff29cfbd20637059b49a343fe53052687beb029ada4d7941f00b2a0b9d40f1190aeb3f80173023f5a53ba43495457cfce48911362147a5c684000e144b9906177b1293b8279dd2f597993b0f8e2bae86c6f2a633aca5d1a77217500ced8389b77c8f3a70473e1aa6b61c1275fa241cf738b4df1ffc92972f3c6a2a100b4873b2c5ef377a83d4d66933911a5706c0a5081ff6e3941d979ed40d60294da00d6c2d1b57bd2516c8974658bb325f6d59223e9cf0e7b4e2b8c65cd54a0b35ade01bc1e21006f5a686abf3d7e3be99b09ae716fe2f31e7f6360413306b03ff9dd9e00c8d1571b7a3d2d28f80ea2b5a4a2887ad85b0c1b8c2435b71c908e45abf4c9780121e84314e351ee1fcce26abd37c78fc38213c2813dd914e52258d0d61df46f750046eafeb76116670abc0c33b6bb475b4c702322c809f7bdd92e46185a8d32f8cb00d5278fffd12598f2d0eeb5ae1ec46ba9bf64d9a8cf9f97e47717915116e2e1e300a722b83b65c0b02efa03bcb6a01bfeea6328c2db08249ed816abc8fcb0485d0c00'


class Borsh:
    def __init__(self, data):
        self.start = 0
        self.data = data

    def fetch(self, size):
        assert self.start + size <= len(self.data)
        chunk = bytes(self.data[self.start:self.start+size])
        self.start += size
        return chunk

    def peekSha256(self, size):
        assert self.start + size <= len(self.data)
        return sha256(self.data[self.start:self.start+size])

    def done(self):
        assert self.start == len(self.data)


T = TypeVar('T', bound='BorshObject')


class BorshObject:
    @classmethod
    @abstractmethod
    def decode(cls: Type[T], data: Borsh) -> T: ...


class bytes32(bytes):
    @classmethod
    def decode(cls, data: Borsh):
        return bytes32(data.fetch(32))


class uint8(int, BorshObject):
    @classmethod
    def decode(cls, data: Borsh):
        value = data.fetch(1)
        return uint8(value[0])


class uint32(int):
    @classmethod
    def decode(cls, data: Borsh):
        value = data.fetch(4)
        return uint32(struct.unpack("I", value)[0])


class uint64(int):
    @classmethod
    def decode(cls, data: Borsh):
        value = data.fetch(8)
        return uint64(struct.unpack("Q", value)[0])


class uint128(int):
    @classmethod
    def decode(cls, data: Borsh):
        hi = uint64.decode(data)
        lo = uint64.decode(data)
        return uint128((hi << 64) | lo)


class BorshBytes:
    @classmethod
    def decode(cls, data: Borsh):
        value = uint32.decode(data)
        return data.fetch(value)


class Bool:
    @classmethod
    def decode(cls, data: Borsh) -> bool:
        value = uint8.decode(data)
        assert 0 <= value < 1
        return value == 1


def sha256(data) -> bytes32:
    return bytes32(hashlib.sha256(data).digest())


def swap4(v: uint32):
    v = ((v & 0x00ff00ff) << 8) | ((v & 0xff00ff00) >> 8)
    return (v << 16) | (v >> 16)


class MerklePathItem:
    hash: bytes32
    direction: uint8

    @ classmethod
    def decode(cls, data: Borsh):
        obj = MerklePathItem()
        obj.hash = bytes32.decode(data)
        obj.direction = uint8.decode(data)
        assert obj.direction < 2
        return obj


class MerklePath:
    items: List[MerklePathItem]

    @ classmethod
    def decode(cls, data: Borsh):
        obj = MerklePath()
        obj.items = decode_list(MerklePathItem, data)
        return obj


class ExecutionStatus:
    enumIndex: uint8
    unknown: Bool
    failed: Bool
    successValue: BorshBytes
    successReceiptId: bytes32

    @classmethod
    def decode(cls, data: Borsh):
        obj = ExecutionStatus()
        obj.enumIndex = uint8.decode(data)
        obj.unknown = Bool.decode(data)
        obj.failed = Bool.decode(data)
        obj.successValue = BorshBytes.decode(data)
        obj.successReceiptId = bytes32.decode(data)
        return obj


def decode_list(T, data: Borsh):
    size = uint32.decode(data)
    result = []
    for _ in range(size):
        result.append(T.decode(data))
    return result


class ExecutionOutcome:
    logs: List[BorshBytes]
    receipt_ids: List[bytes32]
    gas_burnt: uint64
    tokens_burnt: uint128
    executor_id: BorshBytes
    status: ExecutionStatus
    merkelization_hashes: List[bytes32]

    @ classmethod
    def decode(cls, data: Borsh):
        obj = ExecutionOutcome()
        obj.logs = decode_list(BorshBytes, data)

        start = data.start
        obj.receipt_ids = decode_list(bytes32, data)
        obj.gas_burnt = uint64.decode(data)
        obj.tokens_burnt = uint128.decode(data)
        obj.executor_id = BorshBytes.decode(data)
        obj.status = ExecutionStatus.decode(data)

        obj.merkelization_hashes = [sha256(data.data[start:data.start])]
        for log in obj.logs:
            obj.merkelization_hashes.append(sha256(log))
        return obj


class ExecutionOutcomeWithId:
    id: bytes32
    outcome: ExecutionOutcome
    hash: bytes32

    @ classmethod
    def decode(cls, data: Borsh):
        obj = ExecutionOutcomeWithId()
        obj.id = bytes32.decode(data)
        obj.outcome = ExecutionOutcome.decode(data)
        # HERE >>>
        length = 1 + obj.outcome.merkelization_hashes
        # obj.hash =sha256(swap4())
        return obj


class ExecutionOutcomeWithIdAndProof:
    proof: MerklePath
    block_hash: bytes32
    outcome_with_id: ExecutionOutcomeWithId

    @ classmethod
    def decode(cls, data: Borsh):
        obj = ExecutionOutcomeWithIdAndProof()
        obj.proof = MerklePath.decode(data)
        obj.block_hash = bytes32.decode(data)
        obj.outcome_with_id = ExecutionOutcomeWithId.decode(data)
        return obj


class BlockHeaderInnerLite:
    height: uint64
    epoch_id: bytes32
    next_epoch_id: bytes32
    prev_state_root: bytes32
    outcome_root: bytes32
    timestamp: uint64
    next_bp_hash: bytes32
    block_merkle_root: bytes32
    hash: bytes32

    @ classmethod
    def decode(cls, data: Borsh) -> "BlockHeaderInnerLite":
        obj = BlockHeaderInnerLite()
        obj.hash = data.peekSha256(208)
        obj.height = uint64.decode(data)
        obj.epoch_id = bytes32.decode(data)
        obj.next_epoch_id = bytes32.decode(data)
        obj.prev_state_root = bytes32.decode(data)
        obj.outcome_root = bytes32.decode(data)
        obj.timestamp = uint64.decode(data)
        obj.next_bp_hash = bytes32.decode(data)
        obj.block_merkle_root = bytes32.decode(data)
        return obj


class BlockHeaderLight:
    prev_block_hash: bytes32
    inner_rest_hash: bytes32
    inner_lite: BlockHeaderInnerLite
    hash: bytes32

    @ classmethod
    def decode(cls, data: Borsh):
        obj = BlockHeaderLight()
        obj.prev_block_hash = bytes32.decode(data)
        obj.inner_rest_hash = bytes32.decode(data)
        obj.inner_lite = BlockHeaderInnerLite.decode(data)
        obj.hash = sha256(sha256(obj.inner_lite.hash +
                                 obj.inner_rest_hash) + obj.prev_block_hash)
        return obj


class FullOutcomeProof:
    outcome_proof: ExecutionOutcomeWithIdAndProof
    outcome_root_proof: MerklePath
    block_header_lite: BlockHeaderLight
    block_proof: MerklePath

    @ classmethod
    def decode(cls, data: Borsh):
        obj = FullOutcomeProof()
        obj.outcome_proof = ExecutionOutcomeWithIdAndProof.decode(data)
        obj.outcome_root_proof = MerklePath.decode(data)
        obj.block_header_lite = BlockHeaderLight.decode(data)
        obj.block_proof = MerklePath.decode(data)
        return obj


def computeRoot(node: bytes32, proof: MerklePath) -> bytes32:
    hash = node

    for item in proof.items:
        if item.direction == 0:
            hash = sha256(item.hash + hash)
        else:
            hash = sha256(hash, item.hash)

    return hash


def proveOutcome(proofData, blockHeight) -> bool:
    borsh = Borsh(proofData)
    fullOutcomeProof = FullOutcomeProof.decode(borsh)
    borsh.done()

    hash = computeRoot(fullOutcomeProof.outcome_proof.outcome_with_id.hash,
                       fullOutcomeProof.outcome_proof.proof)

    hash = sha256(hash)

    hash = computeRoot(hash, fullOutcomeProof.outcome_root_proof)

    assert hash == fullOutcomeProof.block_header_lite.inner_lite.outcome_root, "NearProver: outcome merkle proof is not valid"

    # expectedBlockMerkleRoot = bridge.blockMerkleRoots(blockHeight)
    expectedBlockMerkleRoot = bytes32()

    assert computeRoot(fullOutcomeProof.block_header_lite.hash,
                       fullOutcomeProof.block_proof) == expectedBlockMerkleRoot, "NearProver: block proof is not valid"

    return True


def main():
    proof = bytes.fromhex(BLOCK_PROOF)
    assert proveOutcome(proof, 57685824)


if __name__ == '__main__':
    main()
