import os
from dotenv import load_dotenv

load_dotenv()

class DBConfig:
    def __init__(self):
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USERNAME')
        self.db_pass = os.getenv('DB_PASSWORD')
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')
        self.ws_address = os.getenv('WEB_SOCKET_URL')
        self.ws_token = os.getenv('WEB_SOCKET_KEY')

db_config = DBConfig()