# generate_secret_key.py
import secrets

secret_key = secrets.token_hex(32)  # Generates a random 32-byte hexadecimal string
print(f"Your secret key is: {secret_key}")
