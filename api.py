import os
from datetime import datetime
from uuid import uuid4

from blockchain import BlockChain
from flask import Flask, request


app = Flask("Blockchain APP")
bc = BlockChain()
node_address = str(uuid4()).replace("-", "")


@app.get("/mine")
def mine():
    start_time = datetime.now()
    block = bc.mine(node_address, os.getenv("BLOCKCHAIN_RECEIVER", "Default"))
    end_time = datetime.now()
    time = (end_time - start_time).total_seconds()
    return {"block": block.get_dict(), "mine_duration": time}


@app.get("/get_chain")
def get_chain():
    return {"chain": [bl.get_dict() for bl in bc.chain]}


@app.get("/verify")
def verify():
    return {"valid": bc.is_chain_valid()}


@app.post("/add_transaction")
def add_transaction():
    json = request.get_json()
    transaction_keys = ["sender", "receiver", "amount"]
    if not all(key in json for key in transaction_keys):
        return f"Some elements of the transaction ({transaction_keys}) are missing", 400
    index = bc.add_transaction(json["sender"], json["receiver"], json["amount"])
    response = {"message": f"This transaction will be added to Block {index}"}
    return response


@app.post("/connect_node")
def connect_node():
    data = request.get_json()
    nodes = data.get("nodes")
    if nodes is None:
        return "No node", 400
    for node in nodes:
        bc.add_node(node)
    return {"total_nodes": list(bc.nodes)}


@app.get("/replace_chain")
def replace_chain():
    is_chain_replaced = bc.replace_chain()
    return {
        "is_chain_replaced": is_chain_replaced,
        "chain": [bl.get_dict() for bl in bc.chain],
    }
