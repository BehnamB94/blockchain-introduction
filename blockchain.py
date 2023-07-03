import json
import hashlib
from datetime import datetime
from urllib.parse import urlparse

import requests


class Transaction:
    def __init__(self, sender: str, receiver: str, amount: int) -> None:
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def get_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
        }

    @staticmethod
    def from_dict(obj: dict) -> "Transaction":
        return Transaction(
            sender=obj["sender"], receiver=obj["receiver"], amount=obj["amount"]
        )


class Block:
    def __init__(
        self,
        index: int,
        timestamp: datetime,
        proof: int,
        previous_hash: str,
        transactions: list[Transaction] = list(),
    ) -> None:
        self.index = index
        self.timestamp = timestamp
        self.proof = proof
        self.previous_hash = previous_hash
        self.transactions = transactions

    def get_dict(self):
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "proof": self.proof,
            "previous_hash": self.previous_hash,
            "transactions": [t.get_dict() for t in self.transactions],
        }

    @staticmethod
    def from_dict(obj: dict) -> "Block":
        return Block(
            index=obj["index"],
            timestamp=obj["timestamp"],
            proof=obj["proof"],
            previous_hash=obj["previous_hash"],
            transactions=[Transaction.from_dict(d) for d in obj["transactions"]],
        )

    def __repr__(self) -> str:
        return json.dumps(self.get_dict(), sort_keys=True)

    def hash(self) -> str:
        encoded_block = self.__repr__().encode()
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
        self.add_transaction(sender, receiver, amount=1)
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

    def add_transaction(self, sender, receiver, amount) -> int:
        self.transactions.append(Transaction(sender, receiver, amount))
        previous_block = self.get_last_block()
        return previous_block.index + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/get_chain")
            if response.status_code == 200:
                chain_dict = response.json()["chain"]
                length = len(chain_dict)
                chain = [Block.from_dict(d) for d in chain_dict]
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
    def get_nonce_bytes(new_proof: int, previous_proof: int):
        return str(new_proof**2 - previous_proof**2).encode()
        # return str(new_proof**3 - previous_proof**3).encode()
        # return str(new_proof + previous_proof).encode()

    @classmethod
    def is_hash_valid(cls, hash: str) -> bool:
        return hash.startswith("0" * cls.number_of_leading_zeros)
