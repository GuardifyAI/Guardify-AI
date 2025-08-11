from app import create_app
from api_handler import ApiHandler

app = create_app()
HOST = "0.0.0.0"
PORT = 8574

if __name__ == "__main__":
    api_handler = ApiHandler(app)
    api_handler.run(HOST, PORT)