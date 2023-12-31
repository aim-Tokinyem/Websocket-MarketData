from price_websocket import WebSocketClient
import sys
from dotenv import load_dotenv
import os

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from datastore.postgre import PostgreStorage


if __name__ == "__main__":
    load_dotenv()
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USERNAME')
    db_pass = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    postgre_storage = PostgreStorage(db_name,db_user,db_pass,db_host,db_port)
    
    ws_address = os.getenv('WEB_SOCKET_URL')
    ws_token = os.getenv('WEB_SOCKET_KEY')

    ticker = postgre_storage.select_ticker()
    all_ticker = [i[2] for i in ticker]
    websocket_client = WebSocketClient(ws_address,ws_token,all_ticker,postgre_storage)

    try:
        websocket_client.start()
    except KeyboardInterrupt:
        websocket_client.ws.close()
        print("Program interrupted. WebSocket connection closed.")