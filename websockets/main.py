from websockets.price_websocket import WebSocketManager
import sys
from dotenv import load_dotenv
import os
import time
from threading import Thread, Event

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from datastore.postgre import PostgreStorage

def poll_for_ticker_updates(interval, get_all_ticker, ws_manager, ws_address, ws_token, postgre_storage, stop_event):
    previous_ticker_list = get_all_ticker()

    while not stop_event.is_set():
        time.sleep(interval)
        current_ticker_list = get_all_ticker()
        
        if current_ticker_list != previous_ticker_list:
            print("Tickers updated. Restarting websocket...")
            ws_manager.stop()
            ws_manager = WebSocketManager(ws_address, ws_token, current_ticker_list, postgre_storage)
            ws_manager.start()
            previous_ticker_list = current_ticker_list

def main():
    load_dotenv()
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USERNAME')
    db_pass = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    postgre_storage = PostgreStorage(db_name, db_user, db_pass, db_host, db_port)

    ws_address = os.getenv('WEB_SOCKET_URL')
    ws_token = os.getenv('WEB_SOCKET_KEY')

    def get_all_ticker():
        ticker = postgre_storage.select_ticker()
        return [i[2] for i in ticker]

    all_ticker = get_all_ticker()
    ws_manager = WebSocketManager(ws_address, ws_token, all_ticker, postgre_storage)

    stop_event = Event()

    # Start the polling thread
    polling_thread = Thread(target=poll_for_ticker_updates, args=(10, get_all_ticker, ws_manager, ws_address, ws_token, postgre_storage, stop_event))
    polling_thread.start()

    while True:
        command = input("Enter command (start/stop/restart/exit): ").strip().lower()

        if command == "start":
            ws_manager.start()
        elif command == "stop":
            ws_manager.stop()
        elif command == "restart":
            ws_manager.stop()
            all_ticker = get_all_ticker()
            ws_manager = WebSocketManager(ws_address, ws_token, all_ticker, postgre_storage)
            ws_manager.start()
        elif command == "exit":
            ws_manager.stop()
            stop_event.set()
            polling_thread.join()
            break
        else:
            print("Invalid command. Please enter 'start', 'stop', 'restart', or 'exit'.")

if __name__ == "__main__":
    main()
