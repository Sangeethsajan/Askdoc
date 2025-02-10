from cryptography.fernet import Fernet
import os

decrypt_key = os.getenv('DECRYPT_KEY')
if not decrypt_key:
    raise Exception("DECRYPT_KEY not found in environment variables")

# Read encrypted content
with open('.env.encrypted', 'rb') as file:
    encrypted_content = file.read()

# Decrypt content
fernet = Fernet(decrypt_key.encode())
decrypted_content = fernet.decrypt(encrypted_content)

# Save to .env file
with open('.env', 'wb') as file:
    file.write(decrypted_content)

print("Environment variables decrypted successfully!")