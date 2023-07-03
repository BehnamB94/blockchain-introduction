import os
from typing import Any
from uuid import uuid4

from flask import Flask, send_from_directory, Response
from flask_pydantic import validate
from pydantic import BaseModel, HttpUrl

from blockchain import BlockChain, Transaction


app = Flask("Blockchain APP")
bc = BlockChain()
node_address = str(uuid4()).replace("-", "")


class AddNodeInput(BaseModel):
    nodes: list[HttpUrl]


class AppResponse(BaseModel):
    status: str = "successful"
    data: Any


def get_receiver() -> str:
    return os.getenv("BLOCKCHAIN_RECEIVER", "Default Receiver")


@app.get("/mine")
@validate()
def mine():
    block = bc.mine(node_address, get_receiver())
    return AppResponse(data={"block": block.model_dump()})


@app.get("/get_chain")
@validate()
def get_chain():
    return AppResponse(data={"chain": [bl.model_dump() for bl in bc.chain]})


@app.get("/verify")
@validate()
def verify():
    return AppResponse(data={"valid": bc.is_chain_valid()})


@app.post("/add_transaction")
@validate()
def add_transaction(body: Transaction):
    index = bc.add_transaction(body)
    return AppResponse(data=f"This transaction will be added to Block {index}")


@app.post("/connect_node")
@validate()
def connect_node(body: AddNodeInput):
    for node in body.nodes:
        bc.add_node(node.unicode_string())
    return AppResponse(data={"total_nodes": list(bc.nodes)})


@app.get("/replace_chain")
@validate()
def replace_chain():
    try:
        is_chain_replaced = bc.replace_chain()
    except Exception as e:
        return AppResponse(status="error", data=str(e)), 500
    return AppResponse(
        data={
            "chain_replaced": is_chain_replaced,
            "chain": [bl.model_dump() for bl in bc.chain],
        }
    )


@app.get("/receiver")
@validate()
def receiver():
    return AppResponse(data=get_receiver())


@app.route("/static/<path:path>")
def send_report(path):
    return send_from_directory("static", path)


@app.get("/")
def ui_html():
    with open("static/index.html") as file:
        return Response(file.read(), mimetype="text/html")
