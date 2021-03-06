import base64
import requests
import subprocess  # nosec B404
import shlex
import xmltodict

from tempfile import TemporaryDirectory as TempD

from django.conf import settings

from .helpers import logger

# GeneraConstancia Payload
REQUEST_CERTIFICATE = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" \
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

# ValidaConstancia Payload
REQUEST_VALIDATE = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" \
xmlns:xw="www.XMLWebServiceSoapHeaderAuth.net">
   <soap:Header>
        <xw:AuthSoapHd>
            <xw:Usuario>{user}</xw:Usuario>
            <xw:Clave>{passwd}</xw:Clave>
            <xw:Entidad>{entity}</xw:Entidad>
        </xw:AuthSoapHd>
   </soap:Header>
   <soap:Body>
      <xw:ValidaConstancia>
         <xw:referencia>{reference}</xw:referencia>
         <xw:constancia>{certificate}</xw:constancia>
      </xw:ValidaConstancia>
   </soap:Body>
</soap:Envelope>"""


class ReachCore:
    """
        Class to handle rich core methods and connections
        referencia = "merkleroot" as a valid str sha256 hash
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

    def generate_proof(self, merkleroot):
        """
            ReachCore endpoint [GeneraConstancia]
            merkleroot : Must be a valid sha256 str, as the merkle root is
        """
        # Generates a temp directory where manipulate docs

        with TempD() as temp_dir:
            doc_path = temp_dir + "/doc_body.tsq"
            request_file = None
            # Prepare the command for the request file
            command = (F"openssl ts -query -digest {merkleroot} -sha256 -no_nonce "
                       F"-tspolicy {self.POLICY} -out {doc_path}")
            args = shlex.split(command)
            try:
                # Pass security params as check=True and shell = False - More details in Bandit B603
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
            body = REQUEST_CERTIFICATE.format(user=self.USER, passwd=self.PASS, entity=self.ENTITY,
                                              reference=merkleroot, doc_base64=request_file)
            # For debug only
            # logger.info(body)

            try:
                # Send requests and get the content
                r = requests.post(self.BASE, data=body, headers=self.HEADERS, timeout=self.TIMEOUT)
                logger.info(F"Response: {r.status_code}")
                logger.info(F"{r.content}")

                if r.status_code == 200:
                    # Parse the file and generate readable json metadata
                    parsed_result = xmltodict.parse(r.text)
                    body = parsed_result["soap:Envelope"]["soap:Body"]
                    metadata = body["GeneraConstanciaResponse"]["GeneraConstanciaResult"]
                    metadata["xml_raw"] = r.text
                    return metadata
                else:
                    # TODO Try to generate next block
                    # Execute a default behauvior or try to do it in other time
                    return None

            except Exception as e:
                logger.error(F"[Generate Proof Error]: {e}, type: {type(e)}, merkleroot: {merkleroot}")

    def validate(self, certificate, merkleroot):
        """ Validate certificate using Reachcore validate endpoints """
        try:
            body = REQUEST_VALIDATE.format(user=self.USER, passwd=self.PASS, entity=self.ENTITY,
                                           reference=merkleroot, certificate=certificate)
            r = requests.post(self.BASE, data=body, headers=self.HEADERS, timeout=self.TIMEOUT)
            logger.info(F"Response: {r.status_code}")
            logger.info(F"{r.content}")
            if r.status_code == 200:
                parsed_result = xmltodict.parse(r.text)
                body = parsed_result["soap:Envelope"]["soap:Body"]
                metadata = body["ValidaConstanciaResponse"]["ValidaConstanciaResult"]
                metadata["xml_raw"] = r.text
                return metadata

            else:
                # We might ask to user to try again
                return None

        except Exception as e:
            logger.error(F"[Validate Certificate Fails]: {e}, type: {type(e)}, merkleroot: {merkleroot}")
