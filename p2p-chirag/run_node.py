from blockchain import Blockchain
from node import Node

def run_node(host, port, peer_host=None, peer_port=None):
    blockchain = Blockchain(difficulty=2)
    node = Node(host, port, blockchain)
    
    # Start node server
    node.start()

    # Optionally connect to a peer node
    if peer_host and peer_port:
        node.connect_to_peer(peer_host, peer_port)

if __name__ == "__main__":
    import sys
    host = sys.argv[1]  # e.g., 'localhost'
    port = int(sys.argv[2])  # e.g., 5000
    peer_host = sys.argv[3] if len(sys.argv) > 3 else None
    peer_port = int(sys.argv[4]) if len(sys.argv) > 4 else None

    run_node(host, port, peer_host, peer_port)
