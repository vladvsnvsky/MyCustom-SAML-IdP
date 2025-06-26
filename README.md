
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

```
## 📁 Project Structure


IdP-SAML/
|  run.py
|  requirements.txt
|  idp_cert.pem
|  idp_private_key.pem
|  app/
|  ├── app.py
|  ├── routes/
|  │   ├── login_route.py
|  │   ├── logout_route.py
|  │   ├── home_route.py
|  │   ├── metadata_route.py
|  │   └── sso_route.py
|  ├── templates/
|  │   ├── login.html
|  │   ├── home.html
|  │   └── page.html
|  └── utils/
|      ├── auth.py
|      ├── saml_utils.py
|      └── session_operations.py

```

---

## ⚙️ .env Setup

```env
METADATA_URL = "http://localhost:5000/metadata"
SIGN_IN_URL = "http://localhost:5000/sso"
PATH_TO_PRIVATE_KEY= "private_key.pem"
PATH_TO_CERTIFICATE = "saml_cert.pem"
YOUR_ENTITY_NAME = "test"
AUTH0_CONNECTION_NAME = "myIdp-Flask"
KEY_TO_ENCODE = "abc123"
TEST_EMAIL = "user1@test.com"
TEST_PASSWORD = "abcd"
ACTIVE_SESSION = "user_id:1829|email:user1@test.org|name:TestFirstName TestLastName|expires:2028-06-20"
```
In the `.env`, ensure the active session is not expired -- update the value of the `expires` field.

---

## ✅ To Run

1. Generate a `private_key.pem` file using the following command:
```
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
```

2. Generate a `saml_cert.pem` using the following command:
```
openssl req -new -x509 -key private_key.pem -out saml_cert.pem -days 365
```
The fill in the prompts

3. Install the dependencies
```
pip install -r requirements.txt
```

4. Start the IdP on the Local Machine
```
python run.py
```
# On Auth0 Side
1. Create an `Auth0 SAML Connection` named `myIdp-Flask`
2. Set a name and the Sign In URL to `http://localhost:5000/sso`
3. Under `Login Experience` tab enable the option `Display connection as a button`
4. Under `Applications`, enable the connection for the Tenant's `Default App`
5. Go to `Getting Started` > Click on `Login Box` > `Try it out` and use the SAML Connection.
---

