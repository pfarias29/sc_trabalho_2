import requests
import os
import time

PORT = 8080
URL = "https://localhost:" + str(PORT)
CERT_FILE_RECEIVED = "received_cert.pem" 

def get_certificado():

    cert = None

    if not os.path.exists(CERT_FILE_RECEIVED):
        open(CERT_FILE_RECEIVED, "w").close()

    with open(CERT_FILE_RECEIVED, "rb") as f:
        cert = f.read()

    if not cert:
        print("Requisitando certificado...")

        url = URL + "/cert"
        response = requests.get(url=url, verify=False)
        if response.status_code == 200:
            with open(CERT_FILE_RECEIVED, "wb") as f:
                f.write(response.content)
            print("Certificado recebido com sucesso!")
            print("Certificaod: "+ response.text)
        else:
            print("Erro ao receber certificado: " + str(response.status_code))
            return None
    else:
        print("Certificado já recebido!")

    return CERT_FILE_RECEIVED


def secure_request():
    cert_file = get_certificado()

    if not cert_file:
        print("Certificado não recebido!")
        return
    print("Requisitando resposta...")
    

    response = requests.get(url=URL, verify=cert_file)
    
    if response.status_code == 200:
        print("Resposta segura recebida com sucesso!\n")
        print(f"Resposta: {response.text}\n")
    else:
        print("Erro ao receber resposta: " + str(response.status_code))
    


if __name__ == "__main__":
    # Requisição GET #
    for _ in range(10):
        secure_request()
        time.sleep(5)