import os
import json

class Config:
    # Network Configuration
    DEFAULT_PORT = 8333
    P2P_PORT = 8334
    WEB_PORT = 5050
    
    # Mining Configuration
    DIFFICULTY_TARGET = 4  # Number of leading zeros required
    BLOCK_TIME_TARGET = 60  # Target block time in seconds (HayX spec)
    MINING_REWARD = 10.0  # HayX block reward
    HALVING_INTERVAL = 525600  # Blocks per halving (~1 year)
    COIN_NAME = 'HayX Coin'
    SYMBOL = 'HX'
    
    # Blockchain Configuration
    GENESIS_REWARD = 1000000.0
    MAX_TRANSACTIONS_PER_BLOCK = 100
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    BLOCKCHAIN_FILE = os.path.join(DATA_DIR, 'blockchain.json')
    PEERS_FILE = os.path.join(DATA_DIR, 'peers.json')
    WALLETS_DIR = os.path.join(DATA_DIR, 'wallets')
    
    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(WALLETS_DIR, exist_ok=True)
    
    # Network Discovery
    BOOTSTRAP_NODES = [
        "127.0.0.1:8334",  # localhost for testing
    ]
    
    # GUI Configuration
    THEME = 'dark'  # 'light' or 'dark'
    AUTO_REFRESH_INTERVAL = 5000  # milliseconds

# Load or create peer list
def load_peers():
    try:
        with open(Config.PEERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return Config.BOOTSTRAP_NODES

def save_peers(peers):
    with open(Config.PEERS_FILE, 'w') as f:
        json.dump(peers, f)
