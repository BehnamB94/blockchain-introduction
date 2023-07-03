import os
from datetime import datetime
from uuid import uuid4

from flask import Flask, request
from flask_pydantic import validate
from pydantic import BaseModel, HttpUrl

from blockchain import BlockChain, Transaction


app = Flask("Blockchain APP")
bc = BlockChain()
node_address = str(uuid4()).replace("-", "")


class AddNodeInput(BaseModel):
    nodes: list[HttpUrl]


@app.get("/mine")
def mine():
    start_time = datetime.now()
    block = bc.mine(node_address, os.getenv("BLOCKCHAIN_RECEIVER", "Default"))
    end_time = datetime.now()
    time = (end_time - start_time).total_seconds()
    return {"block": block.model_dump(), "mine_duration": time}


@app.get("/get_chain")
def get_chain():
    return {"chain": [bl.model_dump() for bl in bc.chain]}


@app.get("/verify")
def verify():
    return {"valid": bc.is_chain_valid()}


@app.post("/add_transaction")
@validate()
def add_transaction(body: Transaction):
    index = bc.add_transaction(body)
    response = {"message": f"This transaction will be added to Block {index}"}
    return response


@app.post("/connect_node")
@validate()
def connect_node(body: AddNodeInput):
    for node in body.nodes:
        bc.add_node(node.unicode_string())
    return {"total_nodes": list(bc.nodes)}


@app.get("/replace_chain")
def replace_chain():
    try:
        is_chain_replaced = bc.replace_chain()
    except Exception as e:
        return {"error": str(e)}, 500
    return {
        "is_chain_replaced": is_chain_replaced,
        "chain": [bl.model_dump() for bl in bc.chain],
    }
