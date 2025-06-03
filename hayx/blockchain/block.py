import json
import hashlib
import time
from .transaction import Transaction

class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate block hash"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        """Mine block using Proof of Work"""
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        print(f"Block mined: {self.hash}")
    
    def to_dict(self):
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create block from dictionary"""
        transactions = [Transaction.from_dict(tx_data) for tx_data in data['transactions']]
        block = cls(data['index'], transactions, data['previous_hash'], data['nonce'])
        block.timestamp = data['timestamp']
        block.hash = data['hash']
        return block
    
    def is_valid(self, previous_block=None):
        """Validate block"""
        # Check hash
        if self.hash != self.calculate_hash():
            return False
        
        # Check previous hash
        if previous_block and self.previous_hash != previous_block.hash:
            return False
        
        # Validate transactions
        for tx in self.transactions:
            if tx.sender != "coinbase" and not tx.signature:
                return False
        
        return True
