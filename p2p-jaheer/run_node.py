import sys
from blockchain import Blockchain
from node import Node

def start_node(host, port, peer_host=None, peer_port=None):
    # Create a new blockchain instance
    blockchain = Blockchain(difficulty=2)  # Adjust difficulty as needed

    # Create a P2P node
    node = Node(host, port, blockchain)

    # Start the server (listening for incoming connections from peers)
    node.start()

    # If peer information is provided, connect to the peer
    if peer_host and peer_port:
        node.connect_to_peer(peer_host, peer_port)
    else:
        print("This node is running standalone, connect peers manually if needed.")

    # Infinite loop to keep the node running
    while True:
        print("\n1. Mine a new block")
        print("2. View the blockchain")
        print("3. Connect to a new peer")
        print("4. Broadcast blockchain to peers")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            # Mine a new block with a simple transaction
            transaction_data = input("Enter transaction data: ")
            blockchain.unconfirmed_transactions.append(transaction_data)
            last_block = blockchain.get_last_block()

            new_block = blockchain.create_new_block(last_block)
            proof = blockchain.proof_of_work(new_block)

            if blockchain.add_block(new_block, proof):
                print(f"Block mined and added: {new_block.__dict__}")
                node.broadcast_block(new_block)
            else:
                print("Failed to mine block")

        elif choice == "2":
            print("\nBlockchain:")
            for block in blockchain.chain:
                print(f"Index: {block.index}, Hash: {block.hash}, Data: {block.data}")

        elif choice == "3":
            peer_host = input("Enter peer host: ")
            peer_port = int(input("Enter peer port: "))
            node.connect_to_peer(peer_host, peer_port)

        elif choice == "4":
            # node.broadcast_block()
            latest_block = node.blockchain.chain[-1] if node.blockchain.chain else None
            if latest_block:
                node.broadcast_block(latest_block)
            else:
                print("No block available to broadcast!")

        elif choice == "5":
            print("Exiting node...")
            sys.exit()

        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_node.py <host> <port> [peer_host] [peer_port]")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    # Optional: If connecting to an existing peer, provide peer host and port
    peer_host = None
    peer_port = None

    if len(sys.argv) == 5:
        peer_host = sys.argv[3]
        peer_port = int(sys.argv[4])

    start_node(host, port, peer_host, peer_port)
