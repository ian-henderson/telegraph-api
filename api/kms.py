from base64 import urlsafe_b64decode, urlsafe_b64encode
import boto3
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet
import logging
from os import getenv


class KmsClient:
    client = boto3.client("kms")

    def __init__(self):
        self.current_data_key = self.get_data_key()

    def decrypt(self, ciphertext: str) -> str or None:
        try:
            data_key, encoded_data = ciphertext.split(":", 1)
            fernet = Fernet(data_key)
            decrypted_data = fernet.decrypt(urlsafe_b64decode(encoded_data))
        except Exception as exception:
            logging.error(f"Decryption Error: {exception}")
            return None

        return decrypted_data.decode("utf-8")

    def encrypt(self, plaintext: str) -> str or None:
        fernet = Fernet(self.current_data_key)

        try:
            encrypted_data = fernet.encrypt(plaintext.encode("utf-8"))
        except Exception as exception:
            logging.error(f"Encryption Error: {exception}")
            return None

        encrypted_string = urlsafe_b64encode(encrypted_data).decode("utf-8")

        return f"{self.current_data_key}:${encrypted_string}"

    def get_data_key(self, key_spec="AES_256"):
        alias_name = getenv("AWS_KMS_KEY_ALIAS_NAME")

        if not alias_name:
            logging.critical("Missing .env var AWS_KMS_KEY_ALIAS_NAME")
            exit(1)

        try:
            response = self.client.generate_data_key(
                KeyId=f"alias/{alias_name}", KeySpec=key_spec
            )
        except ClientError as error:
            logging.critical(f"Failed to generate data key: {error}")
            exit(1)

        logging.info("Created KMS data key.")

        return urlsafe_b64encode(response["Plaintext"]).decode("utf-8")


kms_client = KmsClient()
