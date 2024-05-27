import logging
from logging.handlers import TimedRotatingFileHandler
import os
from dotenv import load_dotenv

class LoggerConfig:
    def __init__(self, log_name):
        load_dotenv()
        self.log_dir = os.getenv('LOG_DIR')
        self.log_name = log_name
        self.full_path = self.log_dir + self.log_name
        self.configure_logging()

    def configure_logging(self):
        os.makedirs(self.full_path, exist_ok=True)  # Create 'logs' directory if it doesn't exist

        log_path = os.path.join(self.full_path, self.log_name + '.log')  # Path to the log file within 'logs' directory
        print(self.log_dir, type(self.log_dir))
        handler = TimedRotatingFileHandler(
            filename=log_path,
            when='midnight',  # Rotate at midnight
            interval=1,  # Create a new log file every day
            backupCount=7  # Retain up to 7 days' worth of logs
        )

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.NOTSET)

# if __name__ == "__main__":
#     pass
#     # logger_config = LoggerConfig('my_app2')
#     # logging.debug('This is a debug message')
#     # logging.info('This is an info message')
#     # logging.warning('This is a warning message')
#     # logging.error('This is an error message')
#     # logging.critical('This is a critical message')