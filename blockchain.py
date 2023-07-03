import hashlib
from datetime import datetime
from urllib.parse import urlparse

import requests
from pydantic import BaseModel, validator


class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: int


class Block(BaseModel):
    index: int
    timestamp: datetime
    proof: int
    previous_hash: str
    transactions: list[Transaction] = list()

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    @validator("timestamp", pre=True)
    def time_validate(cls, v):
        return datetime.fromisoformat(v) if v is str else v

    def hash(self) -> str:
        encoded_block = self.model_dump_json().encode()
        return hashlib.sha3_256(encoded_block).hexdigest()


class BlockChain:
    number_of_leading_zeros = 4

    def __init__(self) -> None:
        self.chain: list[Block] = list()
        self.transactions: list[Transaction] = list()
        self.nodes: set[str] = set()
        self._create_block(proof=1, previous_hash="0")

    def mine(self, sender: str, receiver: str) -> Block:
        last_block = self.get_last_block()
        last_proof = last_block.proof
        new_proof = self._proof_of_work(last_proof)
        new_transaction = Transaction(sender=sender, receiver=receiver, amount=1)
        self.add_transaction(new_transaction)
        return self._create_block(new_proof, last_block.hash())

    def _create_block(self, proof: int, previous_hash: str) -> Block:
        block = Block(
            index=len(self.chain) + 1,
            timestamp=datetime.now(),
            proof=proof,
            previous_hash=previous_hash,
            transactions=self.transactions,
        )
        self.transactions = list()
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

    def is_chain_valid(self, chain: list[Block] | None = None) -> bool:
        if chain is None:
            chain = self.chain
        previous_block = chain[0]
        for block in chain[1:]:
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

    def add_transaction(self, transaction: Transaction) -> int:
        self.transactions.append(transaction)
        previous_block = self.get_last_block()
        return previous_block.index + 1

    def add_node(self, address: str) -> set[str]:
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        return self.nodes

    def replace_chain(self) -> bool:
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/get_chain")
            if response.status_code == 200:
                chain_dict = response.json()["data"]["chain"]
                length = len(chain_dict)
                chain = [Block.model_validate(d) for d in chain_dict]
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    def __repr__(self) -> str:
        return str(self.chain)

    @staticmethod
    def get_nonce_bytes(new_proof: int, previous_proof: int) -> bytes:
        return str(new_proof**2 - previous_proof**2).encode()
        # return str(new_proof**3 - previous_proof**3).encode()
        # return str(new_proof + previous_proof).encode()

    @classmethod
    def is_hash_valid(cls, hash: str) -> bool:
        return hash.startswith("0" * cls.number_of_leading_zeros)
