import hashlib
import time

class Block:
    def __init__(self, index, previous_hash, data, timestamp=None):
        self.index = index                   # Block number
        self.previous_hash = previous_hash   # Hash of the previous block
        self.data = data                     # Block data (transactions)
        self.timestamp = timestamp or time.time()  # Time of block creation
        self.nonce = 0                       # Nonce to be adjusted during mining
        self.hash = self.compute_hash()      # Current hash of this block

    def compute_hash(self):
        """
        Creates a SHA-256 hash of the block's contents.
        """
        block_string = f"{self.index}{self.previous_hash}{self.data}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        """
        Mines the block by adjusting the nonce until the hash starts with the required number of zeros.
        """
        target = '0' * difficulty  
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.compute_hash()
        print(f"Block mined! Hash: {self.hash}")

# usage:
block = Block(index=1, previous_hash='0'*64, data="Some transactions")
print("Mining block...")
block.mine_block(difficulty=4)  

# output
# Mining block...
# Block mined! Hash: 00004c8fa2f3f9c67fa6e67b0a3fbe2a7684eb2907c4b6174b424e9d3f8e5d70
