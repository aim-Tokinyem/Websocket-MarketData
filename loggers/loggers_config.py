"""
This module provides a LoggerConfig class to configure logging
"""

import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime
from dotenv import load_dotenv

# pylint: disable=too-few-public-methods
class LoggerConfig:
    """LoggerConfig sets up a logging configuration with a standard file handler."""
    def __init__(self, log_name):
        load_dotenv()
        self.log_dir = os.getenv('LOG_DIR')
        self.log_name = log_name
        self.full_path = self.log_dir + self.log_name
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.configure_logging()

    def configure_logging(self):
        """Configures the logging settings including the file handlerand log format."""
        os.makedirs(self.full_path, exist_ok=True)  # Create 'logs' directory if it doesn't exist

        log_path = os.path.join(self.full_path,
                                self.log_name +
                                '_' +
                                self.date +
                                '.log')  # Path to the log file within 'logs' directory
        handler = TimedRotatingFileHandler(
            filename=log_path,
            when='midnight',  # Rotate at midnight
            interval=1,  # Create a new log file every day
            backupCount=7  # Retain up to 7 days' worth of logs
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.NOTSET)
