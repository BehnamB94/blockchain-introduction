from datetime import datetime

from blockchain import BlockChain
from flask import Flask


app = Flask("Blockchain APP")
bc = BlockChain()


@app.get("/mine")
def mine():
    last_block = bc.get_last_block()
    last_proof = last_block.proof
    start_time = datetime.now()
    new_proof = bc.proof_of_work(last_proof)
    end_time = datetime.now()
    block = bc.create_block(new_proof, last_block.hash())
    time = (end_time - start_time).total_seconds()
    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "proof": block.proof,
        "hash": block.hash(),
        "previous_hash": block.previous_hash,
        "mine_duration": time,
    }


@app.get("/get_chain")
def get_chain():
    return {"valid": [bl.get_dict() for bl in bc.chain]}


@app.get("/verify")
def verify():
    return {"valid": bc.is_chain_valid()}
