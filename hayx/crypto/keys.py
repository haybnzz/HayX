import hashlib
import ecdsa
from ecdsa import SigningKey, SECP256k1
import binascii
import os

class KeyPair:
    def __init__(self, private_key=None):
        if private_key:
            self.private_key = SigningKey.from_string(
                binascii.unhexlify(private_key), curve=SECP256k1
            )
        else:
            self.private_key = SigningKey.generate(curve=SECP256k1)
        
        self.public_key = self.private_key.get_verifying_key()
    
    def get_private_key_hex(self):
        return binascii.hexlify(self.private_key.to_string()).decode()
    
    def get_public_key_hex(self):
        return binascii.hexlify(self.public_key.to_string()).decode()
    
    def get_address(self):
        """Generate wallet address from public key"""
        public_key_hex = self.get_public_key_hex()
        sha256_hash = hashlib.sha256(public_key_hex.encode()).hexdigest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash.encode())
        return ripemd160.hexdigest()[:20]  # Take first 20 characters
    
    def sign_message(self, message):
        """Sign a message with private key"""
        message_hash = hashlib.sha256(message.encode()).digest()
        signature = self.private_key.sign(message_hash)
        return binascii.hexlify(signature).decode()
    
    def verify_signature(self, message, signature, public_key_hex):
        """Verify signature using public key"""
        try:
            public_key = ecdsa.VerifyingKey.from_string(
                binascii.unhexlify(public_key_hex), curve=SECP256k1
            )
            message_hash = hashlib.sha256(message.encode()).digest()
            return public_key.verify(binascii.unhexlify(signature), message_hash)
        except:
            return False
