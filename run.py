from app.app import app

from dotenv import load_dotenv
import os

load_dotenv()  # this loads the .env file into environment variables

secret = os.getenv("SECRET_KEY")
debug = os.getenv("DEBUG")


if __name__ == "__main__":
    app.run(debug=True)
