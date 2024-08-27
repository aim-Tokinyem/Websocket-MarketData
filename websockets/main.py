"""
Main module for running WebSocket manager.
"""

import argparse
from websockets.price_websocket import WebSocketManager
from datastore.db_config import DBConfig

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Control the WebSocket Manager.")
    parser.add_argument("--command", type=str, help="Command to run: start, stop, restart, exit")
    args = parser.parse_args()

    # Initialize DBConfig and WebSocketManager
    db_config = DBConfig()
    manager = WebSocketManager(db_config)

    # Run the WebSocket manager with the provided command
    manager.run(command=args.command)
