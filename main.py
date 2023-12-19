# from datastore.postgre import PostgreStorage
from price_websocket import WebSocketClient
from datastore.postgre import PostgreStorage
import json
import threading
# def handle_message(message):
#     print(f"Received Message: {message}")
#     # Insert message into the database here

if __name__ == "__main__":

    postgre_storage = PostgreStorage()
    ws_address = "wss://api.tiingo.com/fx"
    websocket_client = WebSocketClient(ws_address,["eurusd","eurnok"],postgre_storage)

    try:
        websocket_client.start()
    except KeyboardInterrupt:
        websocket_client.ws.close()
        print("Program interrupted. WebSocket connection closed.")