import hashlib
import time

class Block:
    def __init__(self, index, previous_hash, data, timestamp=None, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = self.compute_hash()

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
        target = '0' * difficulty  # Create target hash with difficulty number of leading zeros
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.compute_hash()

class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions = []

    def create_genesis_block(self):
        """
        Creates the first block in the blockchain, called the 'genesis block'.
        """
        return Block(0, "0" * 64, "Genesis Block", time.time())

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block):
        """
        Adds a block to the blockchain after validating it.
        """
        previous_block = self.get_last_block()
        if block.previous_hash == previous_block.hash and self.is_valid_block(block, previous_block):
            self.chain.append(block)
        else:
            raise Exception("Invalid block: failed to add to chain.")

    def is_valid_block(self, block, previous_block):
        """
        Validates a block by checking if its hash and previous hash match.
        """
        return (block.hash == block.compute_hash() and 
                block.previous_hash == previous_block.hash)

    def mine_pending_transactions(self, miner_address):
        """
        Mines all pending transactions by creating a new block.
        """
        if not self.pending_transactions:
            print("No transactions to mine.")
            return

        new_block = Block(index=len(self.chain),
                          previous_hash=self.get_last_block().hash,
                          data=self.pending_transactions)
        new_block.mine_block(self.difficulty)
        self.add_block(new_block)

        # Reward the miner for mining the block
        self.pending_transactions = [f"Reward to {miner_address}"]
