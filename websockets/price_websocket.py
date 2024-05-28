import websocket
import simplejson as json
import threading
import time
from loggers.config_logging import LoggerConfig
import logging

logger_config = LoggerConfig('WebSocket')

class WebSocketClient:
    def __init__(self, ws_address, web_socket_token, ticker, postgre_storage):
        self.ws_address = ws_address
        self.ws_token = web_socket_token
        self.ticker = ticker
        self.postgre_storage = postgre_storage
        self.ws = None
        self.thread = None

    def on_message(self, ws, message):
        json_message = json.loads(message)
        print(json_message)
        logging.info(json_message)
        if json_message['messageType'] == "A":
            self.postgre_storage.insert_price(json_message['data'])

    def on_open(self, ws):
        print("WebSocket successfully connected!")
        logging.info("WebSocket successfully connected!")
        self.send_request()

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket is closed")
        logging.info("WebSocket is closed")

    def on_error(self, ws, error):
        self.error = error
        print(f"WebSocket Error {self.error}")
        logging.error(f"WebSocket Error {self.error}")

    def send_request(self):
        subscribe = {
            'eventName': 'subscribe',
            'authorization': self.ws_token,
            'eventData': {
                'tickers': self.ticker,
            }
        }
        self.ws.send(json.dumps(subscribe))

    def start(self):
        if self.ws is not None:
            print("WebSocket is already running")
            return
        self.ws = websocket.WebSocketApp(self.ws_address,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.start()
        print(f"Connecting to WebSocket {self.ws_address}")
        logging.info(f"Connecting to WebSocket {self.ws_address}")

    def stop(self):
        if self.ws is None:
            print("WebSocket is not running")
            return
        self.ws.close()
        self.thread.join()
        self.ws = None
        self.thread = None
        print("WebSocket connection closed")
        logging.info("WebSocket connection closed")

    def restart(self):
        self.stop()
        self.start()

class WebSocketManager:
    def __init__(self, ws_address, ws_token, ticker, postgre_storage):
        self.websocket_client = WebSocketClient(ws_address, ws_token, ticker, postgre_storage)

    def start(self):
        self.websocket_client.start()

    def stop(self):
        self.websocket_client.stop()

    def restart(self):
        self.websocket_client.restart()
