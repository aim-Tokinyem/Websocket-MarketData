""" main.py for server """
from server.server import app

if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask app
