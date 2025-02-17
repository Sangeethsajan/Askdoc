from cryptography.fernet import Fernet
import os

from dotenv import load_dotenv
load_dotenv()

decrypt_key = 'Qm3LzVPgIfiR7b3HAy5FeKQTnfuqDX8PJVO6lhjZXAE='
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