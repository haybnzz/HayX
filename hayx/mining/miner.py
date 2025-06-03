import threading
import time
from hayx.blockchain.blockchain import Blockchain
from hayx.blockchain.transaction import Transaction
from config import Config

class Miner:
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
        self.blockchain = Blockchain()
        self.is_mining = False
        self.mining_thread = None
        self.hash_rate = 0
        self.blocks_mined = 0
        
    def start_mining(self):
        """Start mining process"""
        if not self.is_mining:
            self.is_mining = True
            self.mining_thread = threading.Thread(target=self._mine_loop)
            self.mining_thread.daemon = True
            self.mining_thread.start()
            print(f"Mining started for address: {self.wallet_address}")
    
    def stop_mining(self):
        """Stop mining process"""
        self.is_mining = False
        if self.mining_thread:
            self.mining_thread.join()
        print("Mining stopped")
    
    def _mine_loop(self):
        """Main mining loop"""
        last_hash_time = time.time()
        hash_count = 0
        
        while self.is_mining:
            try:
                # Check if there are pending transactions or mine empty block
                if len(self.blockchain.pending_transactions) > 0:
                    print(f"Mining block with {len(self.blockchain.pending_transactions)} transactions...")
                    
                    start_time = time.time()
                    new_block = self.blockchain.mine_pending_transactions(self.wallet_address)
                    end_time = time.time()
                    
                    self.blocks_mined += 1
                    mining_time = end_time - start_time
                    
                    print(f"Block #{new_block.index} mined successfully!")
                    print(f"Hash: {new_block.hash}")
                    print(f"Mining time: {mining_time:.2f} seconds")
                    print(f"Nonce: {new_block.nonce}")
                    print(f"Reward: {Config.MINING_REWARD} HayX")
                    
                    # Calculate hash rate
                    hash_count = new_block.nonce
                    self.hash_rate = hash_count / mining_time if mining_time > 0 else 0
                    
                else:
                    # No pending transactions, wait a bit
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Mining error: {e}")
                time.sleep(1)
    
    def get_mining_stats(self):
        """Get mining statistics"""
        return {
            'is_mining': self.is_mining,
            'hash_rate': self.hash_rate,
            'blocks_mined': self.blocks_mined,
            'wallet_address': self.wallet_address,
            'difficulty': self.blockchain.difficulty
        }
