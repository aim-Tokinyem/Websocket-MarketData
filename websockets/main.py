from websockets.price_websocket import WebSocketManager

if __name__ == "__main__":
    manager = WebSocketManager()
    manager.run()