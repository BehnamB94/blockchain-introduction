from datetime import datetime

from blockchain import BlockChain
from flask import Flask


app = Flask("Blockchain APP")
bc = BlockChain()


@app.get("/mine")
def mine():
    start_time = datetime.now()
    block = bc.mine()
    end_time = datetime.now()
    time = (end_time - start_time).total_seconds()
    return {"block": block.get_dict(), "mine_duration": time}


@app.get("/get_chain")
def get_chain():
    return {"valid": [bl.get_dict() for bl in bc.chain]}


@app.get("/verify")
def verify():
    return {"valid": bc.is_chain_valid()}
