import base64
import requests

from tempfile import TemporaryDirectory as TempD

from django.conf import settings

from .helpers import logger


body_xml = """
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:xw="www.XMLWebServiceSoapHeaderAuth.net">
    <soap:Header>
        <xw:AuthSoapHd>
            <xw:Usuario>{user}</xw:Usuario>
            <xw:Clave>{passwd}</xw:Clave>
            <xw:Entidad>{entity}</xw:Entidad>
        </xw:AuthSoapHd>
    </soap:Header>
    <soap:Body>
        <xw:GeneraConstancia>
            <xw:referencia>{reference}</xw:referencia>
            <xw:solicitud>{doc_base64}</xw:solicitud>
        </xw:GeneraConstancia>
    </soap:Body>
</soap:Envelope>"""


class ReachCore:
    """
        Class to handle rich core methods and connections
        reference = "Merkle hash"
    """

    ENTITY = settings.REACHCORE_ENTITY
    USER = settings.REACHCORE_USER
    PASS = settings.REACHCORE_PASS

    TIMEOUT = 10
    HEADERS = {'content-type': 'text/xml'}

    def __init__(self, **kwargs):
        """  Initialize vars and settings """

        if settings.PRODUCTION:
            self.BASE = "https://nom151.advantage-security.com/wsnom151/webservice.asmx?WSDL"
        else:
            self.BASE = "https://pilot-psc.reachcore.com/wsnom151/webservice.asmx?WSDL"

    def generate_proof(self, merkle_hash):
        """
            ReachCore endpoint [GeneraConstancia]
            merkle_hash : str type and a valid sha256
        """
        # Generates a temp directory where manipulate docs

        with TempD() as temp_dir:
            doc_path = temp_dir + "/doc_body.tsq"
            request_file = None

            # Create request file and converting to base64 string
            pass

            # Read the file
            with open(doc_path, 'rb') as f:
                request_file = base64.b64encode(f.read())
                request_file = request_file.decode()

            # Create body content
            body = body_xml.format(user=self.USER, passwd=self.PASS, entity=self.ENTITY,
                                   reference=merkle_hash, doc_base64=request_file)

            try:
                # Send requests and get the content
                r = requests.post(self.BASE, data=body, headers=self.HEADERS)

                if r.code_status == 200:
                    # save the file and save in the block the reference
                    pass
                else:
                    # Execute a default behauvior or try to do it in other time
                    pass

            except Exception as e:
                logger.error(F"[Generate Proof Error]: {e}, type: {type(e)}, merkle_hash: {merkle_hash}")
