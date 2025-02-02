import json
import time
import os
from cryptography.fernet import Fernet
from base64 import b64encode
import hashlib

class CredentialManager:
    def __init__(self):
        self.cred_file = os.path.join(os.getenv('APPDATA'), '.parking_creds')
        self.key_file = os.path.join(os.getenv('APPDATA'), '.parking_key')
        self._init_encryption_key()
        
    def _init_encryption_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        self.cipher = Fernet(self.key)

    def save_credentials(self, creds):
        data = {
            'credentials': creds,
            'timestamp': time.time()
        }
        encrypted_data = self.cipher.encrypt(json.dumps(data).encode())
        with open(self.cred_file, 'wb') as f:
            f.write(encrypted_data)

    def load_credentials(self):
        if not os.path.exists(self.cred_file):
            return None
        
        try:
            with open(self.cred_file, 'rb') as f:
                encrypted_data = f.read()
            
            data = json.loads(self.cipher.decrypt(encrypted_data))
            
            if time.time() - data['timestamp'] > 5 * 3600:
                os.remove(self.cred_file)
                return None
                
            return data['credentials']
        except:
            return None

    def clear_credentials(self):
        if os.path.exists(self.cred_file):
            os.remove(self.cred_file)