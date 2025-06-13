from app.app import TEST_PASSWORD, TEST_EMAIL, ACTIVE_SESSIONS
from app.utils.session_operations import encode_session


def signin_email_and_password(email: str, password:str) -> str | None :
    if not isinstance(email, str) or not isinstance(password, str):
        raise Exception("bad credentials")
    if email == TEST_EMAIL and password == TEST_PASSWORD:
        # This is for testing - we keep a decoded session in the active_sessions set
        decoded_session = ACTIVE_SESSIONS[0]
        session = encode_session(decoded_session)
        return session

    return None
