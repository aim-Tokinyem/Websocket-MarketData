import websocket
import simplejson as json
import threading
import time
from loggers.config_logging import LoggerConfig
import logging
import sys
from dotenv import load_dotenv
import os
import time
from threading import Thread, Event
from datastore.postgre import PostgreStorage
from datastore.db_config import db_config

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

class WebSocketManager:
    def __init__(self):
        self.db_name = db_config.db_name
        self.db_user = db_config.db_user
        self.db_pass = db_config.db_pass
        self.db_host = db_config.db_host
        self.db_port = db_config.db_port
        
        self.ws_address = db_config.ws_address
        self.ws_token = db_config.ws_token
        
        self.postgre_storage = PostgreStorage(self.db_name, self.db_user, self.db_pass, self.db_host, self.db_port)
        self.ws_manager = None
        self.stop_event = Event()

    def get_all_ticker(self):
        ticker = self.postgre_storage.select_ticker()
        return [i[2] for i in ticker]

    def poll_for_ticker_updates(self, interval):
        previous_ticker_list = self.get_all_ticker()

        while not self.stop_event.is_set():
            time.sleep(interval)
            current_ticker_list = self.get_all_ticker()
            
            if current_ticker_list != previous_ticker_list:
                print("Tickers updated. Restarting websocket...")
                self.ws_manager.stop()
                self.ws_manager = WebSocketClient(self.ws_address, self.ws_token, current_ticker_list, self.postgre_storage)
                self.ws_manager.start()
                previous_ticker_list = current_ticker_list

    def start_polling(self, interval=10):
        self.polling_thread = Thread(target=self.poll_for_ticker_updates, args=(interval,))
        self.polling_thread.start()

    def start_websocket(self):
        all_ticker = self.get_all_ticker()
        self.ws_manager = WebSocketClient(self.ws_address, self.ws_token, all_ticker, self.postgre_storage)
        self.ws_manager.start()

    def stop_websocket(self):
        if self.ws_manager:
            self.ws_manager.stop()

    def run(self):
        self.start_polling()

        while True:
            command = input("Enter command (start/stop/restart/exit): ").strip().lower()

            if command == "start":
                self.start_websocket()
            elif command == "stop":
                self.stop_websocket()
            elif command == "restart":
                self.stop_websocket()
                self.start_websocket()
            elif command == "exit":
                self.stop_websocket()
                self.stop_event.set()
                self.polling_thread.join()
                break
            else:
                print("Invalid command. Please enter 'start', 'stop', 'restart', or 'exit'.")
