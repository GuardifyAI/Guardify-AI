from app import create_app
from controller import Controller

app = create_app()
HOST = "0.0.0.0"
PORT = 8574

if __name__ == "__main__":
    controller = Controller(app)
    app.run(host=HOST, port=PORT)