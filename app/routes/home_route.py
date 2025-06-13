from flask import render_template, request, make_response, redirect
from app.app import app
from app.utils.session_operations import get_valid_session


@app.route("/", methods=["GET"])
def home():
    encoded_session = request.cookies.get("session")
    if not encoded_session or not get_valid_session(encoded_session):
        resp = make_response(redirect("/login"))
        resp.delete_cookie("session", httponly=True)
        return resp

    return render_template("home.html")
