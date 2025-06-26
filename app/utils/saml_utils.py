import base64
import datetime
import uuid

from lxml import etree
from signxml import XMLSigner, methods

from app.app import PATH_TO_PRIVATE_KEY

NAMESPACES = {
    'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
    'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
    'ds': 'http://www.w3.org/2000/09/xmldsig#'
}

def build_signed_saml_response(acs_url:str, issuer:str, audience:str, name_id:str, attributes:str, cert_path=None):

    now = datetime.datetime.now()
    response_id = "_" + str(uuid.uuid4())
    assertion_id = "_" + str(uuid.uuid4())

    issue_instant = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    not_before = issue_instant
    not_on_or_after = (now + datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Response
    response = etree.Element(
        "{urn:oasis:names:tc:SAML:2.0:protocol}Response",
        nsmap=NAMESPACES,
        ID=response_id,
        Version="2.0",
        IssueInstant=issue_instant,
        Destination=acs_url
    )

    # Response / Issuer
    etree.SubElement(response, "{urn:oasis:names:tc:SAML:2.0:assertion}Issuer").text = issuer

    # Response / Status
    status = etree.SubElement(response, "{urn:oasis:names:tc:SAML:2.0:protocol}Status")
    etree.SubElement(status, "{urn:oasis:names:tc:SAML:2.0:protocol}StatusCode",
                     Value="urn:oasis:names:tc:SAML:2.0:status:Success")

    # Response / Assertion
    assertion = etree.SubElement(response, "{urn:oasis:names:tc:SAML:2.0:assertion}Assertion",
                                 ID=assertion_id, Version="2.0", IssueInstant=issue_instant)

    # Response / Assertion / Issuer
    etree.SubElement(assertion, "{urn:oasis:names:tc:SAML:2.0:assertion}Issuer").text = issuer

    # Response / Assertion / Subject
    subject = etree.SubElement(assertion, "{urn:oasis:names:tc:SAML:2.0:assertion}Subject")

    # Response / Assertion / Subject / NameID
    name_id_el = etree.SubElement(subject, "{urn:oasis:names:tc:SAML:2.0:assertion}NameID",
                                  Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent")
    name_id_el.text = name_id

    # Response / Assertion / Subject / SubjectConfirmation
    subject_confirmation = etree.SubElement(subject, "{urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmation",
                                            Method="urn:oasis:names:tc:SAML:2.0:cm:bearer")

    # Response / Assertion / Subject / SubjectConfirmation / SubjectConfirmationData
    etree.SubElement(subject_confirmation,
                     "{urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationData",
                     NotOnOrAfter=not_on_or_after, Recipient=acs_url)

    # Response / Assertion / Conditions
    conditions = etree.SubElement(assertion, "{urn:oasis:names:tc:SAML:2.0:assertion}Conditions",
                                  NotBefore=not_before, NotOnOrAfter=not_on_or_after)

    # Response / Assertion / Conditions / AudienceRestrictions
    audience_restriction = etree.SubElement(conditions, "{urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestriction")

    # Response / Assertion / Conditions / AudienceRestrictions / Audience
    print("audience: ", audience)
    etree.SubElement(audience_restriction, "{urn:oasis:names:tc:SAML:2.0:assertion}Audience").text = audience

    # Response / Assertion / AuthnStatement
    authn_statement = etree.SubElement(assertion, "{urn:oasis:names:tc:SAML:2.0:assertion}AuthnStatement",
                                       AuthnInstant=issue_instant, SessionIndex=assertion_id)

    # Response / Assertion / AuthnStatement / AuthnContext
    authn_context = etree.SubElement(authn_statement, "{urn:oasis:names:tc:SAML:2.0:assertion}AuthnContext")

    # Response / Assertion / AuthnStatement / AuthnContext / AuthnContextClassRef
    etree.SubElement(authn_context, "{urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextClassRef").text = \
        "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"

    # Response / Assertion / AttributeStatement
    if attributes:
        attr_stmt = etree.SubElement(assertion, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement")
        for attr_name, attr_value in attributes.items():
            attr = etree.SubElement(attr_stmt, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute", Name=attr_name)

            if isinstance(attr_value, dict):
                for k, v in attr_value.items():
                    if v is True:
                        val = etree.SubElement(attr, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
                        val.text = str(k)
            elif isinstance(attr_value, (set, list, tuple)):
                for item in attr_value:
                    val = etree.SubElement(attr, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
                    val.text = str(item)
            else:
                val = etree.SubElement(attr, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
                val.text = str(attr_value)

    # Convert full response tree to bytes
    unsigned_xml = etree.tostring(response)

    # Sign with the separate method
    signed_xml = sign_xml(unsigned_xml, cert_path)

    return base64.b64encode(signed_xml).decode("utf-8")

def sign_xml(xml_bytes, cert_path=None):
    # Load private key
    with open(PATH_TO_PRIVATE_KEY, 'rb') as key_file:
        key_data = key_file.read()

    # load X.509 certificate if you want to include it in the signature
    cert_data = None
    if cert_path:
        with open(cert_path, 'rb') as cert_file:
            cert_data = cert_file.read()

    # Parse the XML
    xml = etree.fromstring(xml_bytes)

    # Sign the XML with an enveloped signature
    signer = XMLSigner(method=methods.enveloped, signature_algorithm="rsa-sha256", digest_algorithm="sha256",c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
    signed_xml = signer.sign(xml, key=key_data, cert=cert_data)

    return etree.tostring(signed_xml, pretty_print=False)
