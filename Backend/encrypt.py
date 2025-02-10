from cryptography.fernet import Fernet
import os

# Generate encryption key
key = Fernet.generate_key()
print(f"Your decryption key: {key.decode()}")

# Read the original .env file
with open('.env', 'rb') as file:
    env_content = file.read()

# Encrypt the content
fernet = Fernet(key)
encrypted_content = fernet.encrypt(env_content)

# Save encrypted content
with open('.env.encrypted', 'wb') as file:
    file.write(encrypted_content)

print("Environment variables encrypted successfully!")