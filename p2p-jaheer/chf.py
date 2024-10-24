import hashlib
import time
import random

class ChameleonHash:
    def __init__(self, g, h, p, secret_key):
        self.g = g  # Generator g
        self.h = h  # Generator h
        self.p = p  # Large prime number for the cyclic group
        self.secret_key = secret_key  # Secret key (trapdoor)
    
    def hash(self, data, r):
        """
        Compute the Chameleon Hash using the provided data and randomness r.
        H(data, r) = g^data * h^r (mod p)
        """
        g_pow_data = pow(self.g, data, self.p)
        h_pow_r = pow(self.h, r, self.p)
        return (g_pow_data * h_pow_r) % self.p

    def find_collision(self, old_data, new_data, old_r):
        """
        Given the old data, new data, and old randomness r, find new randomness r'
        that keeps the hash unchanged using the secret key (trapdoor).
        """
        delta_data = new_data - old_data
        inverse_secret = pow(self.secret_key, -1, self.p - 1)  # secret_key^-1 mod (p-1)
        r_prime = (old_r + (delta_data * inverse_secret) % (self.p - 1)) % (self.p - 1)
        return r_prime

class Block:
    def __init__(self, index, previous_hash, data, chameleon_hash, r=None, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.chameleon_hash = chameleon_hash
        self.r = r or random.randint(1, chameleon_hash.p - 1)  # Random value for CHF
        self.timestamp = timestamp or time.time()
        self.hash = self.compute_chameleon_hash()

    def compute_chameleon_hash(self):
        """
        Compute the Chameleon Hash of the block's data.
        """
        return self.chameleon_hash.hash(self.data, self.r)

    def redact_block(self, new_data, secret_key, provided_key):
        """
        Redact the block's data using Chameleon Hash, keeping the hash unchanged.
        Only allowed if the provided key matches the admin's secret key.
        """
        if secret_key != provided_key:
            raise PermissionError("Invalid secret key. Redaction not allowed.")
        
        # Find new randomness that keeps the hash unchanged
        new_r = self.chameleon_hash.find_collision(self.data, new_data, self.r)
        
        # Update the block's data and randomness, but keep the hash the same
        self.data = new_data
        self.r = new_r
        self.hash = self.compute_chameleon_hash()

class Blockchain:
    def __init__(self, chameleon_hash):
        self.chain = []
        self.chameleon_hash = chameleon_hash
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", 0, self.chameleon_hash, random.randint(1, self.chameleon_hash.p - 1))
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_block = self.get_last_block()
        new_block = Block(index=previous_block.index + 1,
                          previous_hash=previous_block.hash,
                          data=data,
                          chameleon_hash=self.chameleon_hash,
                          timestamp=time.time())
        self.chain.append(new_block)

    def is_chain_valid(self):
        """
        Validate the entire chain by checking hashes and previous hash links.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block.compute_chameleon_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def redact_block(self, block_index, new_data, provided_key):
        """
        Redact a block's data if the user has the correct secret key and propagate
        the hash changes forward using the Chameleon Hash function.
        """
        if block_index >= len(self.chain):
            raise IndexError("Block index out of range.")

        block_to_redact = self.chain[block_index]
        block_to_redact.redact_block(new_data, self.chameleon_hash.secret_key, provided_key)
        


# Define group parameters for the Chameleon Hash
g = 2
h = 5
p = 101  # A small prime for simplicity
secret_key = 45  # Admin secret key

# Initialize the Chameleon Hash function
chf = ChameleonHash(g, h, p, secret_key)

# Create a new blockchain using Chameleon Hash
blockchain = Blockchain(chf)

# Add a few blocks
blockchain.add_block(10)
blockchain.add_block(20)
blockchain.add_block(30)

# Print original blockchain
print("Original Blockchain:")
for block in blockchain.chain:
    print(f"Block {block.index} [Hash: {block.hash}] | Data: {block.data}")

# Redact block 1 with new data, while keeping the hash unchanged
try:
    blockchain.redact_block(1, 999, provided_key=secret_key)
except PermissionError as e:
    print(e)

# Print updated blockchain after redaction
print("\nBlockchain After Redaction (Hash unchanged):")
for block in blockchain.chain:
    print(f"Block {block.index} [Hash: {block.hash}] | Data: {block.data}")

# Validate the blockchain after redaction
print("\nIs blockchain valid?", blockchain.is_chain_valid())
