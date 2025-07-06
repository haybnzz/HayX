import threading
import time
from datetime import datetime, timedelta
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
        self.last_block_time = None
        self.hash_rate_history = []
        self.mining_reward = 1.0  # 1 HayX per block
        self.target_block_time = 60  # Target 1 block per minute
        
    def start_mining(self):
        """Start mining process"""
        if not self.is_mining:
            self.is_mining = True
            self.mining_thread = threading.Thread(target=self._mine_loop)
            self.mining_thread.daemon = True
            self.mining_thread.start()
            print(f"⛏️ Mining started for address: {self.wallet_address}")
    
    def stop_mining(self):
        """Stop mining process"""
        self.is_mining = False
        if self.mining_thread:
            self.mining_thread.join()
        print("🛑 Mining stopped")
    
    def _mine_loop(self):
        """Main mining loop with improved algorithm"""
        last_hash_time = time.time()
        hash_count = 0
        block_start_time = time.time()
        
        while self.is_mining:
            try:
                # Calculate current difficulty based on target block time
                self._adjust_difficulty()
                
                # Check if there are pending transactions or mine empty block
                if len(self.blockchain.pending_transactions) > 0:
                    print(f"⛏️ Mining block with {len(self.blockchain.pending_transactions)} transactions...")
                    
                    start_time = time.time()
                    new_block = self.blockchain.mine_pending_transactions(self.wallet_address)
                    end_time = time.time()
                    
                    if new_block:
                        self.blocks_mined += 1
                        mining_time = end_time - start_time
                        self.last_block_time = datetime.now()
                        
                        # Calculate hash rate
                        hash_count = new_block.nonce
                        self.hash_rate = hash_count / mining_time if mining_time > 0 else 0
                        
                        # Add to history
                        self._add_hash_rate_to_history(self.hash_rate)
                        
                        print(f"✅ Block #{new_block.index} mined successfully!")
                        print(f"Hash: {new_block.hash[:16]}...")
                        print(f"Mining time: {mining_time:.2f} seconds")
                        print(f"Nonce: {new_block.nonce}")
                        print(f"Reward: {self.mining_reward} HayX")
                        print(f"Hash rate: {self.hash_rate:.2f} H/s")
                        
                        # Reset block timer
                        block_start_time = time.time()
                    else:
                        print("❌ Failed to mine block")
                        time.sleep(1)
                        
                else:
                    # No pending transactions, mine empty block after target time
                    elapsed_time = time.time() - block_start_time
                    if elapsed_time >= self.target_block_time:
                        print("⛏️ Mining empty block (no pending transactions)...")
                        
                        start_time = time.time()
                        new_block = self.blockchain.mine_empty_block(self.wallet_address)
                        end_time = time.time()
                        
                        if new_block:
                            self.blocks_mined += 1
                            mining_time = end_time - start_time
                            self.last_block_time = datetime.now()
                            
                            # Calculate hash rate
                            hash_count = new_block.nonce
                            self.hash_rate = hash_count / mining_time if mining_time > 0 else 0
                            
                            # Add to history
                            self._add_hash_rate_to_history(self.hash_rate)
                            
                            print(f"✅ Empty block #{new_block.index} mined!")
                            print(f"Hash rate: {self.hash_rate:.2f} H/s")
                            
                            # Reset block timer
                            block_start_time = time.time()
                        else:
                            print("❌ Failed to mine empty block")
                            time.sleep(1)
                    else:
                        # Simulate hash rate while waiting
                        time.sleep(0.1)
                        hash_count += 1000  # Simulate hashing
                        self.hash_rate = hash_count / (time.time() - last_hash_time) if (time.time() - last_hash_time) > 0 else 0
                        
            except Exception as e:
                print(f"❌ Mining error: {e}")
                time.sleep(1)
    
    def _adjust_difficulty(self):
        """Adjust difficulty based on target block time"""
        if self.last_block_time:
            time_since_last_block = (datetime.now() - self.last_block_time).total_seconds()
            
            if time_since_last_block < self.target_block_time * 0.5:
                # Blocks are being mined too fast, increase difficulty
                self.blockchain.difficulty = min(self.blockchain.difficulty + 1, 10)
                print(f"📈 Increased difficulty to {self.blockchain.difficulty}")
            elif time_since_last_block > self.target_block_time * 2:
                # Blocks are taking too long, decrease difficulty
                self.blockchain.difficulty = max(self.blockchain.difficulty - 1, 1)
                print(f"📉 Decreased difficulty to {self.blockchain.difficulty}")
    
    def _add_hash_rate_to_history(self, hash_rate):
        """Add hash rate to history for charting"""
        self.hash_rate_history.append({
            'timestamp': datetime.now().isoformat(),
            'hash_rate': round(hash_rate, 2)
        })
        
        # Keep only last 50 entries
        if len(self.hash_rate_history) > 50:
            self.hash_rate_history.pop(0)
    
    def get_mining_stats(self):
        """Get comprehensive mining statistics"""
        return {
            'is_mining': self.is_mining,
            'hash_rate': self.hash_rate,
            'blocks_mined': self.blocks_mined,
            'wallet_address': self.wallet_address,
            'difficulty': self.blockchain.difficulty,
            'total_rewards': self.blocks_mined * self.mining_reward,
            'last_block_time': self.last_block_time.isoformat() if self.last_block_time else None,
            'target_block_time': self.target_block_time,
            'mining_reward': self.mining_reward,
            'hash_rate_history': self.hash_rate_history[-20:] if self.hash_rate_history else []
        }
