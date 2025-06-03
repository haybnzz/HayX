import json
import os
from .keys import KeyPair
from config import Config

class Wallet:
    def __init__(self, name="default"):
        self.name = name
        self.wallet_file = os.path.join(Config.WALLETS_DIR, f"{name}.json")
        self.keypair = None
        self.balance = 0.0
        self.transactions = []
        
        self.load_or_create()
    
    def load_or_create(self):
        """Load existing wallet or create new one"""
        if os.path.exists(self.wallet_file):
            self.load_wallet()
        else:
            self.create_wallet()
    
    def create_wallet(self):
        """Create new wallet with keypair"""
        self.keypair = KeyPair()
        self.save_wallet()
    
    def load_wallet(self):
        """Load wallet from file"""
        with open(self.wallet_file, 'r') as f:
            data = json.load(f)
            self.keypair = KeyPair(data['private_key'])
            self.balance = data.get('balance', 0.0)
            self.transactions = data.get('transactions', [])
    
    def save_wallet(self):
        """Save wallet to file"""
        data = {
            'name': self.name,
            'private_key': self.keypair.get_private_key_hex(),
            'public_key': self.keypair.get_public_key_hex(),
            'address': self.get_address(),
            'balance': self.balance,
            'transactions': self.transactions
        }
        
        with open(self.wallet_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_address(self):
        """Get wallet address"""
        return self.keypair.get_address()
    
    def get_public_key(self):
        """Get public key"""
        return self.keypair.get_public_key_hex()
    
    def sign_transaction(self, message):
        """Sign transaction"""
        return self.keypair.sign_message(message)
    
    def update_balance(self, amount):
        """Update wallet balance"""
        self.balance += amount
        self.save_wallet()
    
    def add_transaction(self, transaction):
        """Add transaction to history"""
        self.transactions.append(transaction)
        self.save_wallet()
    
    @staticmethod
    def list_wallets():
        """List all available wallets"""
        wallets = []
        for file in os.listdir(Config.WALLETS_DIR):
            if file.endswith('.json'):
                wallets.append(file[:-5])  # Remove .json extension
        return wallets
