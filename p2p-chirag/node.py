import socket
import threading
import json

class Node:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers = []
        
    def start(self):
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Node started on {self.host}:{self.port} and listening for peers...")
        
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_peer, args=(conn, addr)).start()

    def handle_peer(self, conn, addr):
        print(f"Connected by {addr}")
        data = conn.recv(1024).decode()
        if data:
            self.handle_message(data, conn)

    def handle_message(self, message, conn):
        try:
            message = json.loads(message)
            if message['type'] == 'block':
                self.receive_block(message['block'])
            elif message['type'] == 'transaction':
                self.receive_transaction(message['transaction'])
        except Exception as e:
            print(f"Error processing message: {e}")
        conn.close()

    def connect_to_peer(self, peer_host, peer_port):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_host, peer_port))
            self.peers.append((peer_host, peer_port))
            print(f"Connected to peer {peer_host}:{peer_port}")
        except Exception as e:
            print(f"Failed to connect to peer {peer_host}:{peer_port}: {e}")

    def send_to_peers(self, message):
        for peer in self.peers:
            try:
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect(peer)
                peer_socket.sendall(message.encode())
                peer_socket.close()
            except Exception as e:
                print(f"Error sending message to peer {peer}: {e}")

    def receive_block(self, block):
        print(f"Received new block from peer: {block}")
        self.blockchain.add_block(block)

    def receive_transaction(self, transaction):
        print(f"Received new transaction: {transaction}")
        self.broadcast_transaction(transaction)

    def broadcast_block(self, block):
        message = json.dumps({"type": "block", "block": block})
        self.send_to_peers(message)

    def broadcast_transaction(self, transaction):
        message = json.dumps({"type": "transaction", "transaction": transaction})
        self.send_to_peers(message)
