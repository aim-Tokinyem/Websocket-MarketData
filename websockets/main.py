"""
Main module for running WebSocket manager.
"""

from websockets.price_websocket import WebSocketManager
from datastore.db_config import DBConfig


if __name__ == "__main__":
    db_config = DBConfig()
    manager = WebSocketManager(db_config)
    manager.run()
