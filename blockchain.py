from datetime import datetime
from hashlib import sha3_256
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
    nonce: int
    previous_hash: str
    transactions: list[Transaction] = list()

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    @validator("timestamp", pre=True)
    def time_validate(cls, v):
        return datetime.fromisoformat(v) if v is str else v

    def model_dump(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        d["hash"] = self.hash()
        return d

    def hash(self) -> str:
        return sha3_256(self.model_dump_json().encode()).hexdigest()


class BlockChain:
    leading_zero_hex = 4

    def __init__(self) -> None:
        self._chain: list[Block] = list()
        self._transactions: list[Transaction] = list()
        self._nodes: set[str] = set()
        block = self._generate_test_block(nonce=1, prev_hash="0", transactions=[])
        self._add_block(block)

    def mine(self, sender: str, receiver: str) -> Block:
        reward = Transaction(sender=sender, receiver=receiver, amount=1)
        new_block = self._proof_of_work(reward)
        self._add_block(new_block)
        return new_block

    def get_last_block(self) -> Block:
        return self._chain[-1]

    def get_chain_dict(self) -> list[dict]:
        return [bl.model_dump() for bl in self._chain]

    def is_chain_valid(self, chain: list[Block] | None = None) -> bool:
        if chain is None:
            chain = self._chain
        previous_block = chain[0]
        for block in chain[1:]:
            if block.previous_hash != previous_block.hash() or not self.is_hash_valid(
                block.hash()
            ):
                return False
            previous_block = block
        return True

    def add_transaction(self, transaction: Transaction) -> int:
        self._transactions.append(transaction)
        previous_block = self.get_last_block()
        return previous_block.index + 1

    def add_node(self, address: str) -> set[str]:
        parsed_url = urlparse(address)
        self._nodes.add(parsed_url.netloc)
        return self._nodes

    def get_node_list(self) -> list[str]:
        return list(self._nodes)

    def replace_chain(self) -> bool:
        network = self._nodes
        longest_chain = None
        max_length = len(self._chain)
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
            self._chain = longest_chain
            return True
        return False

    def _proof_of_work(self, reward: Transaction) -> Block:
        n = 0
        previous_hash = self.get_last_block().hash()
        transactions = self._transactions + [reward]
        while True:
            candidate_block = self._generate_test_block(n, previous_hash, transactions)
            if self.is_hash_valid(candidate_block.hash()):
                return candidate_block
            else:
                n += 1

    def _generate_test_block(
        self, nonce: int, prev_hash: str, transactions: list[Transaction]
    ) -> Block:
        block = Block(
            index=len(self._chain) + 1,
            timestamp=datetime.now().replace(microsecond=0),
            nonce=nonce,
            previous_hash=prev_hash,
            transactions=transactions,
        )
        return block

    def _add_block(self, block: Block) -> bool:
        if self.is_chain_valid(self._chain + [block]):
            self._transactions = list()
            self._chain.append(block)
            return True
        return False

    def __repr__(self) -> str:
        return str(self._chain)

    @classmethod
    def is_hash_valid(cls, hash: str) -> bool:
        return hash.startswith("0" * cls.leading_zero_hex)
