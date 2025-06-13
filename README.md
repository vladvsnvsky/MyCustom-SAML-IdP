
# MyCustomIDP – SAML Identity Provider (Flask)

A minimal custom **SAML 2.0 Identity Provider** built in **Python (Flask)** that integrates with **Auth0** or any SP. It issues signed SAMLResponses based on login credentials and session cookies.

---

## Features

- `/login`: HTML login form with optional SAML query params
- `/sso`: Accepts `SAMLRequest`, validates session, sends signed SAMLResponse
- `/metadata`: Exposes SAML metadata XML
- `/logout`: Clears session cookie
- HTML pages for:
  - Login UI
  - Home page
  - Manual SAML request testing (`/sso` tester)

---

## 🧩 Routes

| Route        | Method | Description                                 |
|--------------|--------|---------------------------------------------|
| `/login`     | GET/POST | User login with email/password             |
| `/sso`       | GET/POST | Handles SAML SSO logic and sends Response |
| `/metadata`  | GET    | Returns SAML metadata in XML                |
| `/logout`    | GET/POST | Logs out (cookie cleared)                  |
| `/`          | GET    | Protected home page                         |

---

## 🔐 Session Handling

Sessions are stored as encrypted cookies using the secret key (`KEY_TO_ENCODE`) and are verified through helper functions in `session_operations.py`.

For testing purposes, a mock session is preloaded on the server via the `ACTIVE_SESSIONS` list in `app.py`. This allows the Identity Provider to operate without connecting to a real database.

```python
ACTIVE_SESSIONS = [
    "user_id:1829|email:user1@test.com|name:TestFirstName TestLastName|expires:2025-06-15"
]
# Make sure the expiration date is set in the future relative to the current date

```
## 📁 Project Structure

```
app/
├── app.py
├── routes/
│   ├── login_route.py
│   ├── logout_route.py
│   ├── home_route.py
│   ├── metadata_route.py
│   └── sso_route.py
├── templates/
│   ├── login.html
│   ├── home.html
│   └── page.html
└── utils/
    ├── auth.py
    ├── saml_utils.py
    └── session_operations.py
```

---

## ⚙️ .env Setup

```env
METADATA_URL=http://localhost:5000/metadata
SIGN_IN_URL=http://localhost:5000/sso
YOUR_ENTITY_NAME=MyCustomIDP
PATH_TO_PRIVATE_KEY=./certs/private.key
PATH_TO_CERTIFICATE=./certs/public.crt
AUTH0_CONNECTION_NAME= myIdp-Flask
KEY_TO_ENCODE=my_secret_key
TEST_EMAIL=user1@test.com
TEST_PASSWORD=abcd
```

---

## ✅ To Run

```bash
pip install flask
export FLASK_APP=app.py
flask run
```

---

## 🧪 Manual SAML Testing

Use `/sso` with `page.html` to test SAML flows:
- Paste a `SAMLRequest`, `RelayState`, etc.
- Decode and inspect the request
- Submit to see the signed `SAMLResponse`
