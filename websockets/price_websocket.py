"""Module for managing WebSocket connections."""

import threading
import time
import logging
from threading import Thread, Event
import websocket
import simplejson as json
from loggers.loggers_config import LoggerConfig
from datastore.postgre import PostgreStorage
from datastore.db_config import DBConfig

logger_config = LoggerConfig('WebSocket')

class WebSocketClient:
    """Handles WebSocket client connections."""

    def __init__(self, ws_address, web_socket_token, ticker, postgre_storage):
        self.ws_address = ws_address
        self.ws_token = web_socket_token
        self.ticker = ticker
        self.postgre_storage = postgre_storage
        self.ws = None
        self.thread = None
        self.error = None

    def on_message(self, _, message):
        """Handles incoming WebSocket messages."""
        json_message = json.loads(message)
        print(json_message)
        logging.info(json_message)
        if json_message['messageType'] == "A":
            self.postgre_storage.insert_price(json_message['data'])

    def on_open(self, _): # ws
        """Handles WebSocket opening."""
        print("WebSocket successfully connected!")
        logging.info("WebSocket successfully connected!")
        self.send_request()

    def on_close(self, _, __, ___): # ws, close_status_code, close_msg
        """Handles WebSocket closing."""
        print("WebSocket is closed")
        logging.info("WebSocket is closed")

    def on_error(self, _, error):
        """Handles WebSocket errors."""
        self.error = error
        print("WebSocket Error %e", self.error)
        logging.error("WebSocket Error %e", self.error)

    def send_request(self):
        """Sends request over WebSocket."""
        subscribe = {
            'eventName': 'subscribe',
            'authorization': self.ws_token,
            'eventData': {
                'tickers': self.ticker,
            }
        }
        self.ws.send(json.dumps(subscribe))

    def start(self):
        """Starts the WebSocket client."""
        if self.ws is not None:
            print("WebSocket is already running")
            logging.info("WebSocket is already running")
            return
        self.ws = websocket.WebSocketApp(self.ws_address,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.start()
        print("Connecting to WebSocket %s", self.ws_address)
        logging.info("Connecting to WebSocket %s", self.ws_address)

    def stop(self):
        """Stops the WebSocket client."""
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
    """Manages WebSocket connections."""

    def __init__(self, db_config: DBConfig):
        self.db_config = db_config
        self.ws_address = db_config.ws_address
        self.ws_token = db_config.ws_token
        self.postgre_storage = PostgreStorage(self.db_config)
        self.ws_manager = None
        self.stop_event = Event()
        self.polling_thread = None

    def get_all_ticker(self):
        """Retrieves all ticker information."""
        ticker = self.postgre_storage.select_ticker()
        return [i[2] for i in ticker]

    def poll_for_ticker_updates(self, interval):
        """Polls for ticker updates."""
        previous_ticker_list = self.get_all_ticker()

        while not self.stop_event.is_set():
            time.sleep(interval)
            current_ticker_list = self.get_all_ticker()

            if current_ticker_list != previous_ticker_list:
                print("Tickers updated. Restarting websocket...")
                logging.info("Tickers updated. Restarting websocket...")
                self.ws_manager.stop()
                self.ws_manager = WebSocketClient(self.ws_address,
                                                  self.ws_token,
                                                  current_ticker_list,
                                                  self.postgre_storage)
                self.ws_manager.start()
                previous_ticker_list = current_ticker_list

    def start_polling(self, interval=10):
        """Starts polling for ticker updates."""
        self.polling_thread = Thread(target=self.poll_for_ticker_updates, args=(interval,))
        self.polling_thread.start()

    def start_websocket(self):
        """Starts WebSocket."""
        all_ticker = self.get_all_ticker()
        self.ws_manager = WebSocketClient(self.ws_address,
                                          self.ws_token,
                                          all_ticker,
                                          self.postgre_storage)
        self.ws_manager.start()

    def stop_websocket(self):
        """Stops WebSocket."""
        if self.ws_manager:
            self.ws_manager.stop()

    def run(self):
        """Runs WebSocket manager."""
        self.start_polling()

        while True:
            command = input("Enter command (start/stop/restart/exit): ").strip().lower()

            if command == "start":
                logging.info("Starting websocket...")
                self.start_websocket()
            elif command == "stop":
                logging.info("Pause websocket...")
                self.stop_websocket()
            elif command == "restart":
                logging.info("Restarting websocket...")
                self.stop_websocket()
                self.start_websocket()
            elif command == "exit":
                logging.info("Stop websocket...")
                self.stop_websocket()
                self.stop_event.set()
                self.polling_thread.join()
                break
            else:
                logging.error("""Invalid command. Please enter 'start',
                                                            'stop',
                                                            'restart',
                                                            or 'exit'.""")
                print("Invalid command. Please enter 'start', 'stop', 'restart', or 'exit'.")
