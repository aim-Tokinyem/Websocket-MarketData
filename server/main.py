""" main.py for server """
from server.server import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")  # Run the Flask app
