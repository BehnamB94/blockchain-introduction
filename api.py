import os
from datetime import datetime
from typing import Any
from uuid import uuid4

from flask import Flask
from flask_pydantic import validate
from pydantic import BaseModel, HttpUrl

from blockchain import BlockChain, Transaction


app = Flask("Blockchain APP")
bc = BlockChain()
node_address = str(uuid4()).replace("-", "")


class AddNodeInput(BaseModel):
    nodes: list[HttpUrl]


class Response(BaseModel):
    status: str = "successful"
    data: Any


@app.get("/mine")
@validate()
def mine():
    block = bc.mine(node_address, os.getenv("BLOCKCHAIN_RECEIVER", "Default"))
    return Response(data={"block": block.model_dump()})


@app.get("/get_chain")
@validate()
def get_chain():
    return Response(data={"chain": [bl.model_dump() for bl in bc.chain]})


@app.get("/verify")
@validate()
def verify():
    return Response(data={"valid": bc.is_chain_valid()})


@app.post("/add_transaction")
@validate()
def add_transaction(body: Transaction):
    index = bc.add_transaction(body)
    return Response(data=f"This transaction will be added to Block {index}")


@app.post("/connect_node")
@validate()
def connect_node(body: AddNodeInput):
    for node in body.nodes:
        bc.add_node(node.unicode_string())
    return Response(data={"total_nodes": list(bc.nodes)})


@app.get("/replace_chain")
@validate()
def replace_chain():
    try:
        is_chain_replaced = bc.replace_chain()
    except Exception as e:
        return Response(status="error", data=str(e)), 500
    return Response(
        data={
            "chain_replaced": is_chain_replaced,
            "chain": [bl.model_dump() for bl in bc.chain],
        }
    )
