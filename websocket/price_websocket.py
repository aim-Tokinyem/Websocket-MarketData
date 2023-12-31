import websocket
import simplejson as json
import threading
import time

class WebSocketClient:
    def __init__(self, ws_address, web_socket_token, ticker,  postgre_storage):
        self.ws_address = ws_address
        self.ws = websocket.WebSocketApp(ws_address,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ticker = ticker
        self.postgre_storage = postgre_storage
        self.web_socket_token=web_socket_token

    def on_message(self, ws, message):
        json_message = json.loads(message)
        print(json_message)
        if json_message['messageType'] == "A":
            self.postgre_storage.insert_price(json_message['data'])

    def on_open(self, ws):
        print("WebSocket successfully connected!")
        self.send_request()

    def on_close(self, ws, close_status_code, close_ms):
        print("WebSocket is closed")
    
    def on_error(self, ws, error):
        print(f"WebSocket Error {error}")

    def send_request(self):
        subscribe = {
            'eventName': 'subscribe',
            'authorization': self.web_socket_token,
            'eventData': {
                'tickers': self.ticker,
            }
        }
        self.ws.send(json.dumps(subscribe))

    def start(self):
        print(f"Connecting to WebSocket {self.ws_address}")
        try:
            self.ws.run_forever()
        except KeyboardInterrupt:
            self.ws.close()
            print("WebSocket connection closed due to KeyboardInterrupt")

