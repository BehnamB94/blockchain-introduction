from datetime import datetime

import matplotlib.pyplot as plt
from tqdm import tqdm

from blockchain import BlockChain

blocks_to_mine = 100
BlockChain.number_of_leading_zeros = 4

print("=" * 80)
print(f"Start Mining {blocks_to_mine} Block(s)")

bc = BlockChain()
proof_list = list()
time_list = list()
for i in tqdm(range(blocks_to_mine), bar_format="{l_bar}{bar:40}{r_bar}{bar:-10b}"):
    last_block = bc.get_last_block()
    last_proof = last_block.proof
    start_time = datetime.now()
    new_proof = bc.proof_of_work(last_proof)
    end_time = datetime.now()
    bc.create_block(new_proof, last_block.hash())
    time = (end_time - start_time).total_seconds()
    proof_list.append(new_proof)
    time_list.append(time)

print("Finished. Is a valid chain:", bc.is_chain_valid())
print("=" * 80)

plt.hist(proof_list, bins=100)
plt.title("Histogram of Mined Proofs")
plt.show()

plt.plot(time_list)
plt.show()
