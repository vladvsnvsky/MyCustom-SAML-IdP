import os

from flask import Flask

app = Flask(__name__)

METADATA_URL = os.getenv("METADATA_URL")
SIGN_IN_URL = os.getenv("SIGN_IN_URL")
PATH_TO_PRIVATE_KEY= os.getenv("PATH_TO_PRIVATE_KEY")
PATH_TO_CERTIFICATE = os.getenv("PATH_TO_CERTIFICATE")
YOUR_ENTITY_NAME = os.getenv("YOUR_ENTITY_NAME")
AUTH0_CONNECTION_NAME = os.getenv("AUTH0_CONNECTION_NAME")
KEY_TO_ENCODE = os.getenv("KEY_TO_ENCODE")
TEST_EMAIL = os.getenv("TEST_EMAIL")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")
ACTIVE_SESSIONS = [
    "user_id:1829|email:testuser@test.org|name:TestFirstName TestLastName|expires:2025-06-15"
]

# Ensure all routes are imported so they register on app
from app.routes import home_route, metadata_route, sso_route, login_route, logout_route





