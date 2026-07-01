import base64
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

def generate_timestamp():
    curr_datetime = datetime.datetime.now()
    timestamp = curr_datetime.timestamp()
    curr_time_miliseconds = int(timestamp * 1000)
    return str(curr_time_miliseconds)

def load_private_key_from_file(file_path: str):
    with open(file_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # or provide a password if your key is encrypted
            backend=default_backend()
        )
    return private_key

def create_signature(private_key: str, method: str, path: str, timestamp: str):
    # Strip query parameters before signing
    path_without_query = path.split('?')[0]
    message = f"{timestamp}{method}{path_without_query}".encode('utf-8')
    signature = private_key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def package_header(api_key_id: str, generated_signature: str, timestamp: str, content_type=None):

    auth_header = {
        "KALSHI-ACCESS-KEY": api_key_id,
        "KALSHI-ACCESS-SIGNATURE": generated_signature,
        "KALSHI-ACCESS-TIMESTAMP": timestamp
    }

    if content_type:
        auth_header["Content-Type"] = content_type

    return auth_header