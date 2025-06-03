import hashlib
import json

def calculate_hash(index, timestamp, transactions, previous_hash, nonce):
    """Calculate the SHA-256 hash of a block."""
    block_string = json.dumps({
        'index': index,
        'timestamp': timestamp,
        'transactions': [tx.to_dict() for tx in transactions],
        'previous_hash': previous_hash,
        'nonce': nonce
    }, sort_keys=True)
    return hashlib.sha256(block_string.encode()).hexdigest()

def mine_block(index, transactions, previous_hash, difficulty, timestamp):
    """
    Perform proof of work:
    Find a nonce such that the block hash has `difficulty` leading zeroes.
    """
    nonce = 0
    target = '0' * difficulty
    while True:
        hash_value = calculate_hash(index, timestamp, transactions, previous_hash, nonce)
        if hash_value.startswith(target):
            return nonce, hash_value
        nonce += 1
