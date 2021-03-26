import base64
import requests
import subprocess  # nosec B404
import shlex
import xmltodict

from tempfile import TemporaryDirectory as TempD

from django.conf import settings

from .helpers import logger


body_xml = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" \
xmlns:xw="www.XMLWebServiceSoapHeaderAuth.net">
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
        referencia = "merkle_root" as a valid str sha256 hash
        solicitud = doc_file as a valid base64 str
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
            self.POLICY = "2.16.484.101.10.316.2.1.1.2.1"
        else:
            self.BASE = "https://pilot-psc.reachcore.com/wsnom151/webservice.asmx?WSDL"
            self.POLICY = "1.16.484.101.10.316.1.2"

    def generate_proof(self, merkle_hash):
        # TODO change merkle_hash as merkle_root
        """
            ReachCore endpoint [GeneraConstancia]
            merkle_hash : Must be a valid sha256 str, as the merkle root is
        """
        # Generates a temp directory where manipulate docs

        with TempD() as temp_dir:
            doc_path = temp_dir + "/doc_body.tsq"
            request_file = None
            # Prepare the command for the request file
            command = (F"openssl ts -query -digest {merkle_hash} -sha256 -no_nonce "
                       F"-tspolicy {self.POLICY} -out {doc_path}")
            args = shlex.split(command)
            try:
                # Pass security params as check=True and shell=False - More details in Bandit B603
                process = subprocess.run(args, check=True, shell=False)  # nosec B603
            except Exception as e:
                logger.info(F"[Error:{e} Generating File Request], stdout={process.stdout}")
                return None
            else:
                logger.info("Success Generated Request File")
                

            # Read the file
            with open(doc_path, 'rb') as f:
                request_file = base64.b64encode(f.read())
                request_file = request_file.decode()

            # Create body content
            body = body_xml.format(user=self.USER, passwd=self.PASS, entity=self.ENTITY,
                                   reference=merkle_hash, doc_base64=request_file)
            # For debug only
            # logger.info(body)

            try:
                # Send requests and get the content
                r = requests.post(self.BASE, data=body, headers=self.HEADERS, timeout=self.TIMEOUT)
                logger.info(F"Response: {r.status_code}")
                logger.info(F"{r.content}")

                if r.status_code == 200:
                    # Save the file and save in the block the reference
                    parsed_result = xmltodict.parse(r.text)
                    soap = parsed_result["soap:Envelope"]["soap:Body"]
                    metadata = soap["GeneraConstanciaResponse"]["GeneraConstanciaResult"]
                    metadata["xml_raw"] = r.text
                    return metadata
                else:
                    # TODO Try to generate next block 
                    # Execute a default behauvior or try to do it in other time
                    return None

            except Exception as e:
                logger.error(F"[Generate Proof Error]: {e}, type: {type(e)}, merkle_hash: {merkle_hash}")
