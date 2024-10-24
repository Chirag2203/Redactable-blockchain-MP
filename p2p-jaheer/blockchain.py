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
        block_string = f"{self.index}{self.previous_hash}{self.data}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.compute_hash()

class Blockchain:
    def __init__(self, difficulty):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.unconfirmed_transactions = []  

    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block", time.time())

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        last_block = self.get_last_block()
        if last_block.hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        self.chain.append(block)
        return True

    def proof_of_work(self, block):
        block.mine_block(self.difficulty)
        return block.hash

    def is_valid_proof(self, block, block_hash):
        return block_hash.startswith('0' * self.difficulty) and block_hash == block.compute_hash()

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.compute_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def resolve_conflicts(self, chains):
        """
        Simple consensus algorithm: Replace with the longest valid chain
        """
        longest_chain = None
        max_length = len(self.chain)

        for chain in chains:
            if len(chain) > max_length and self.is_chain_valid(chain):
                max_length = len(chain)
                longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False
