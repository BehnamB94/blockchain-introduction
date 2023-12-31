from datetime import datetime

import matplotlib.pyplot as plt
from tqdm import tqdm

from blockchain import BlockChain

blocks_to_mine = 100
BlockChain.leading_zero_hex = 3

print("=" * 80)
print(f"Start Mining {blocks_to_mine} Block(s)")

bc = BlockChain()
time_list = list()
for i in tqdm(range(blocks_to_mine), bar_format="{l_bar}{bar:40}{r_bar}{bar:-10b}"):
    start_time = datetime.now()
    block = bc.mine("A", "B")
    end_time = datetime.now()
    time = (end_time - start_time).total_seconds()
    time_list.append(time)

print("Finished. Is a valid chain:", bc.is_chain_valid())
print("=" * 80)

plt.figure(figsize=(8, 4.5))
plt.boxplot(time_list, vert=False)
plt.title("Distribution of Block Mining Durations")
plt.xlabel("Duration (seconds)")
plt.yticks([])
plt.show()
