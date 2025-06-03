import json
import hashlib
import time
from hayx.crypto.keys import KeyPair

class Transaction:
    def __init__(self, sender, recipient, amount, fee=0.01):
        self.sender = sender
        self.recipient = recipient
        self.amount = float(amount)
        self.fee = float(fee)
        self.timestamp = time.time()
        self.signature = None
        self.tx_id = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate transaction hash"""
        tx_string = f"{self.sender}{self.recipient}{self.amount}{self.fee}{self.timestamp}"
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def sign_transaction(self, private_key_hex):
        """Sign transaction with sender's private key"""
        if self.sender == "coinbase":  # Mining reward transaction
            return True
            
        keypair = KeyPair(private_key_hex)
        message = f"{self.sender}{self.recipient}{self.amount}{self.fee}"
        self.signature = keypair.sign_message(message)
        return True
    
    def verify_signature(self, public_key_hex):
        """Verify transaction signature"""
        if self.sender == "coinbase":  # Mining reward is always valid
            return True
            
        if not self.signature:
            return False
            
        keypair = KeyPair()
        message = f"{self.sender}{self.recipient}{self.amount}{self.fee}"
        return keypair.verify_signature(message, self.signature, public_key_hex)
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'tx_id': self.tx_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'fee': self.fee,
            'timestamp': self.timestamp,
            'signature': self.signature
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create transaction from dictionary"""
        tx = cls(data['sender'], data['recipient'], data['amount'], data['fee'])
        tx.tx_id = data['tx_id']
        tx.timestamp = data['timestamp']
        tx.signature = data.get('signature')
        return tx
    
    def __str__(self):
        return f"TX: {self.sender} -> {self.recipient}: {self.amount} HayX"
