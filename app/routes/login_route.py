from flask import render_template, request, redirect, jsonify, make_response
from urllib.parse import quote
from app.app import app
from app.utils.auth import signin_email_and_password
from app.utils.session_operations import get_valid_session


@app.route("/login", methods=["GET","POST"])
def login_page():
    print("--------------" + request.method + "/login")
    data = request.args if request.method == "GET" else request.form
    saml_request_b64 = data.get("SAMLRequest", "")
    relay_state = data.get("RelayState", "")
    sig_alg = data.get("SigAlg", "")
    signature = data.get("Signature", "")
    query_params = (
            "?SAMLRequest=" + quote(saml_request_b64 or '') +
            "&RelayState=" + quote(relay_state or '') +
            "&SigAlg=" + quote(sig_alg or '') +
            "&Signature=" + quote(signature or '')
    )
    print("Query params: ", query_params)

    encoded_session = request.cookies.get("session")
    session = get_valid_session(encoded_session)

    sso_url = "/sso" + query_params

    if session:
        return redirect(sso_url)

    if request.method == "GET":
        return render_template("login.html")

    # POST logic

    email = request.form.get("email")
    password = request.form.get("password")

    print("User credentials: " + email + " " + password)

    try:
        encoded_session = signin_email_and_password(email, password)
        print("sso_url: " + sso_url)
        if encoded_session:
            resp = make_response(redirect(sso_url))
            resp.set_cookie("session", encoded_session, httponly=True)
            return resp
        else:
            return jsonify({
                "session": None,
                "status": "failed",
                "message": "Authentication failed."
            })

    except :
        return jsonify({
            "session": None,
            "status": "failed",
            "message": "Server error"
        })


