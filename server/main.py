from server.server import app  
# from loggers.config_logging import LoggerConfig

# logger_config = LoggerConfig('Server')

if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask app