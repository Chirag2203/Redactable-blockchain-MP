import socket
import threading
import json
from blockchain import Blockchain, Block

class Node:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers = []
        
    def start(self):
        """
        Starts the node's server and begins listening for peer connections.
        """
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()

    def start_server(self):
        """
        Start a server socket to listen for incoming peer connections.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Node started at {self.host}:{self.port}. Waiting for connections...")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_peer, args=(conn, addr)).start()

    def handle_peer(self, conn, addr):
        """
        Handles the connection with a peer, and processes incoming data (blocks or transactions).
        """
        print(f"Connected by {addr}")
        data = conn.recv(1024).decode()
        if data:
            self.handle_message(data, conn)
        conn.close()

    def handle_message(self, message, conn):
        """
        Processes messages (blocks, transactions) sent by peers.
        """
        try:
            message = json.loads(message)
            if message['type'] == 'block':
                self.receive_block(message['block'])
            elif message['type'] == 'transaction':
                self.receive_transaction(message['transaction'])
        except Exception as e:
            print(f"Error processing message: {e}")

    def receive_block(self, block_data):
        """
        Receives a new block from a peer, validates its PoW, and adds it to the blockchain.
        """
        new_block = Block(block_data['index'], block_data['previous_hash'], block_data['data'], 
                          block_data['timestamp'], block_data['nonce'])
        if new_block.compute_hash() == new_block.hash and new_block.hash.startswith('0' * self.blockchain.difficulty):
            try:
                self.blockchain.add_block(new_block)
                print(f"Block added to the chain: {new_block.hash}")
            except Exception as e:
                print(f"Block validation failed: {e}")
        else:
            print(f"Invalid block received: {new_block.hash}")

    def receive_transaction(self, transaction):
        """
        Receives a transaction and adds it to the pending transactions.
        """
        self.blockchain.pending_transactions.append(transaction)
        print(f"Transaction received: {transaction}")

    def mine_block(self, miner_address):
        """
        Mines a new block, adds it to the blockchain, and broadcasts it to peers.
        """
        print("Mining a new block...")
        if not self.blockchain.pending_transactions:
            print("No transactions to mine.")
            return

        # Mine the block with pending transactions
        last_block = self.blockchain.get_last_block()
        new_block = Block(index=last_block.index + 1,
                          previous_hash=last_block.hash,
                          data=self.blockchain.pending_transactions)
        
        new_block.mine_block(self.blockchain.difficulty)

        # Add the mined block to the blockchain
        self.blockchain.add_block(new_block)

        # Clear the pending transactions (since they've been added to the mined block)
        self.blockchain.pending_transactions = []

        # Broadcast the mined block to peers
        self.broadcast_block(new_block)

    def broadcast_block(self, block):
        """
        Broadcasts the new block to all connected peers.
        """
        message = json.dumps({"type": "block", "block": block.__dict__})
        self.send_to_peers(message)

    def broadcast_transaction(self, transaction):
        """
        Broadcasts a transaction to all connected peers.
        """
        message = json.dumps({"type": "transaction", "transaction": transaction})
        self.send_to_peers(message)

    def send_to_peers(self, message):
        """
        Sends a message to all connected peers.
        """
        for peer in self.peers:
            try:
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect(peer)
                peer_socket.sendall(message.encode())
                peer_socket.close()
            except Exception as e:
                print(f"Error sending message to peer {peer}: {e}")

    def connect_to_peer(self, peer_host, peer_port):
        """
        Connects to a peer and adds it to the list of peers.
        """
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_host, peer_port))
            self.peers.append((peer_host, peer_port))
            print(f"Connected to peer at {peer_host}:{peer_port}")
        except Exception as e:
            print(f"Failed to connect to peer: {e}")
