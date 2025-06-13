from flask import Response
from app.app import app, PATH_TO_CERTIFICATE, YOUR_ENTITY_NAME, SIGN_IN_URL


@app.route("/metadata", methods=["GET"])
def metadata():
    # Path to certificate file
    cert_path = PATH_TO_CERTIFICATE
    # Read and clean certificate
    with open(cert_path, 'r') as cert_file:
        lines = cert_file.readlines()
        cert_base64 = ''.join(
            line.strip() for line in lines
            if "BEGIN CERTIFICATE" not in line and "END CERTIFICATE" not in line
        )

    # Build metadata XML
    metadata_xml = f"""<?xml version="1.0"?>
<EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata" 
                  entityID="{YOUR_ENTITY_NAME}">
    <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <KeyDescriptor use="signing">
            <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#">
                <X509Data>
                    <X509Certificate>{cert_base64}</X509Certificate>
                </X509Data>
            </KeyInfo>
        </KeyDescriptor>
        <SingleSignOnService 
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            Location="{SIGN_IN_URL}"/>
    </IDPSSODescriptor>
</EntityDescriptor>"""

    return Response(metadata_xml, mimetype="application/xml")

