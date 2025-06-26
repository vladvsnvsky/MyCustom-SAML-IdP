import base64
import os
import zlib
import xml.etree.ElementTree as ET
from urllib.parse import quote
from flask import request, render_template_string, redirect, make_response, render_template
from app.app import app, AUTH0_CONNECTION_NAME, METADATA_URL, AUTH0_DOMAIN
from app.utils.saml_utils import build_signed_saml_response
from app.utils.session_operations import get_valid_session, parse_decoded_session

@app.route("/sso", methods=["GET", "POST"])
def sso():
    print("------------SSO----------------------------------------")
    print(request.method)
    # Get params from request.args (GET) or request.form (POST)
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

    encoded_session = request.cookies.get("session")

    login_url = "/login"+query_params

    if not encoded_session:
        return redirect(login_url)


    decoded_session = get_valid_session(encoded_session)

    if not decoded_session:
        print("redirect to login because decoded_session is not valid")
        return redirect(login_url)
    else:
        if request.method == "GET":
            return render_template("page.html")

    if not(relay_state and saml_request_b64 and sig_alg and signature):
        response = make_response(redirect('/'))
        response.set_cookie('session', encoded_session,httponly=True)
        return response

    # Decode SAMLRequest
    try:
        saml_request_xml_string = zlib.decompress(
            base64.b64decode(saml_request_b64), -15
        ).decode()

        print(saml_request_xml_string)
    except Exception:
        saml_request_xml_string = base64.b64decode(saml_request_b64).decode()

    root = ET.fromstring(saml_request_xml_string)
    acs_url = root.attrib.get("AssertionConsumerServiceURL")

    if not acs_url:
        acs_url = f"https://{os.getenv("AUTH0_DOMAIN")}/login/callback?connection={os.getenv("AUTH0_CONNECTION_NAME")}"

    session_data = parse_decoded_session(decoded_session)
    name_id = session_data.get("user_id")
    issuer = METADATA_URL

    attributes = {
        "my_own_user_id": name_id,
        "customAttribute1": "myTest-1",
        "customAttribute2": "myTest-2",
        "roles": {"ADMIN", "HR_MANAGER", "TEST_ROLE"}
    }

    issuer_from_request = root.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Issuer")

    print(f"acs_url: {acs_url if acs_url else 'missing'}")


    saml_response_b64 = build_signed_saml_response(
        acs_url=acs_url,
        issuer=issuer,
        audience = issuer_from_request.text if issuer_from_request is not None else "",
        name_id=name_id,
        attributes=attributes
    )

    return render_template_string("""
    <html>
      <body onload="document.forms[0].submit()">
        <form method="POST" action="{{ acs_url }}">
          <input type="hidden" name="SAMLResponse" value="{{ saml_response }}">
          <input type="hidden" name="RelayState" value="{{ relay_state }}">
        </form>
      </body>
    </html>
    """, acs_url=acs_url, saml_response=saml_response_b64, relay_state=relay_state)
