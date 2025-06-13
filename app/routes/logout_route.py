from flask import request, redirect, make_response

from app.app import app



@app.route("/logout", methods=["GET","POST"])
def logout():
    """
        The logout is done only at the application level.
        The session is stored in the *ACTIVE_SESSIONS* from app.enviroment
    """
    resp = make_response(redirect("/login"))
    resp.delete_cookie("session", httponly=True)

    return resp
