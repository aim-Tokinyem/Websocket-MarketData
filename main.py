# from datastore.postgre import PostgreStorage
from price_websocket import WebSocketClient
from datastore.postgre import PostgreStorage
import json
import threading

if __name__ == "__main__":

    postgre_storage = PostgreStorage()
    ticker = postgre_storage.select_ticker()
    all_ticker = [i[2] for i in ticker]
    ws_address = "wss://api.tiingo.com/fx"
    websocket_client = WebSocketClient(ws_address,all_ticker,postgre_storage)

    try:
        websocket_client.start()
    except KeyboardInterrupt:
        websocket_client.ws.close()
        print("Program interrupted. WebSocket connection closed.")