import json
import hashlib
from datetime import datetime
from typing import List


class Block:
    def __init__(
        self, index: int, timestamp: datetime, proof: int, previous_hash: str
    ) -> None:
        self.index = index
        self.timestamp = timestamp
        self.proof = proof
        self.previous_hash = previous_hash

    def get_dict(self):
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "proof": self.proof,
            "previous_hash": self.previous_hash,
        }

    def __repr__(self) -> str:
        return json.dumps(self.get_dict(), sort_keys=True)

    def hash(self) -> str:
        encoded_block = self.__repr__().encode()
        return hashlib.sha3_256(encoded_block).hexdigest()


class BlockChain:
    number_of_leading_zeros = 4

    def __init__(self) -> None:
        self.chain: List[Block] = list()
        self._create_block(proof=1, previous_hash="0")

    def mine(self) -> Block:
        last_block = self.get_last_block()
        last_proof = last_block.proof
        new_proof = self._proof_of_work(last_proof)
        return self._create_block(new_proof, last_block.hash())

    def _create_block(self, proof: int, previous_hash: str) -> Block:
        block = Block(
            index=len(self.chain) + 1,
            timestamp=datetime.now(),
            proof=proof,
            previous_hash=previous_hash,
        )
        self.chain.append(block)
        return block

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def _proof_of_work(self, previous_proof: int):
        new_proof = 1
        check_proof = False
        while not check_proof:
            nonce_bytes = self.get_nonce_bytes(new_proof, previous_proof)
            hash = hashlib.sha3_256(nonce_bytes).hexdigest()
            if self.is_hash_valid(hash):
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def is_chain_valid(self) -> bool:
        previous_block = self.chain[0]
        for block in self.chain[1:]:
            if block.previous_hash != previous_block.hash():
                return False
            previous_proof = previous_block.proof
            proof = block.proof
            nonce_bytes = self.get_nonce_bytes(proof, previous_proof)
            hash = hashlib.sha3_256(nonce_bytes).hexdigest()
            if not self.is_hash_valid(hash):
                return False
            previous_block = block
        return True

    def __repr__(self) -> str:
        return str(self.chain)

    @staticmethod
    def get_nonce_bytes(new_proof: int, previous_proof: int):
        return str(new_proof**2 - previous_proof**2).encode()
        # return str(new_proof**3 - previous_proof**3).encode()
        # return str(new_proof + previous_proof).encode()

    @classmethod
    def is_hash_valid(cls, hash: str) -> bool:
        return hash.startswith("0" * cls.number_of_leading_zeros)
