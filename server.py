import http.server as server
import ssl
import cryptography.hazmat.primitives.hashes as hashes
import cryptography.hazmat.primitives.asymmetric.rsa as rsa
import cryptography.hazmat.primitives.serialization as serialization
import cryptography.x509 as x509
import datetime as dt
import os

KEY_FILE = "server.key"
CERT_FILE = "server.pem"
PORT = 8080

## Geração de chave e certificado ##

# Geração de chave privada #
def generate_key(public_exponent, key_size):
    return rsa.generate_private_key(public_exponent=public_exponent, key_size=key_size)

# Informações do certificado #
def generate_cert(key):

    cert = 0

    if not os.path.exists(CERT_FILE):
        open(CERT_FILE, "w").close()

    with open(CERT_FILE, "rb") as f:
        cert = f.read()

    # Se já existe um certificado, retorna ele, se não, gera um novo #
    if cert:
        return cert

    subject = issuer = x509.Name([
        x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "BR"),
        x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "Brasília"),
        x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "Cidade"),
        x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "UnB"),
        x509.NameAttribute(x509.NameOID.COMMON_NAME, "localhost"),
    ])

    # Geração do certificado #
    certificado = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(dt.datetime.now())
        .not_valid_after(dt.datetime.now() + dt.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
        .sign(key, hashes.SHA256())
    )

    with open(KEY_FILE, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(CERT_FILE, "wb") as f:
        f.write(certificado.public_bytes(serialization.Encoding.PEM))

class MySimpleHTTPRequestHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path ==  "/cert":
            with open(CERT_FILE, "rb") as f:
                self.send_response(200)
                self.send_header("Content-type", "application/x-x509-ca-cert")
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Mensagem segura!")
    
if __name__ == "__main__":
    key = generate_key(public_exponent=65537, key_size=4096)

    generate_cert(key)

    server_address = ('localhost', PORT)
    httpd = server.HTTPServer(server_address, MySimpleHTTPRequestHandler)

    # Configura o SSL para o servidor
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.set_ecdh_curve("secp384r1")
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Servidor HTTPS rodando em https://localhost:{PORT}")
    httpd.serve_forever()
