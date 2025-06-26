from datetime import datetime, timezone
import base64
import hashlib
from cryptography.fernet import Fernet

from app.app import ACTIVE_SESSIONS, KEY_TO_ENCODE


def get_valid_session(encoded_session):

    try:
        decoded = decode_session(encoded_session)
        if session_is_valid(decoded) and decoded in ACTIVE_SESSIONS:
            return decoded
    except Exception as e:
        pass
    return None

def session_is_valid(session: str) -> bool:
    try:
        parts = session.split("|")
        session_data = dict(p.split(":", 1) for p in parts)
        expires = session_data.get("expires")
        if not expires:
            return False
        expires_dt = datetime.strptime(expires, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return expires_dt >= datetime.now(timezone.utc)
    except Exception as e:
        return False

def _get_fernet():
    key = hashlib.sha256(KEY_TO_ENCODE.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)

def encode_session(session):
    f = _get_fernet()
    encodedSession = f.encrypt(session.encode()).decode()  # string
    return encodedSession

def decode_session(encoded_session):
    f = _get_fernet()
    session = f.decrypt(encoded_session.encode()).decode()  # string
    print("decode_session() returns " + session)
    return session

def parse_decoded_session(decoded_session):
    parts = decoded_session.split("|")
    session_data = dict(p.split(":", 1) for p in parts)
    return session_data