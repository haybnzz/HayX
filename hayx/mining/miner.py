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
        self.total_hash_count = 0
        self.mining_start_time = None
        
    def start_mining(self):
        """Start mining process"""
        if not self.is_mining:
            self.is_mining = True
            self.mining_start_time = time.time()
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
                
                # Simulate hash rate while mining
                hash_count += 1000  # Simulate 1000 hashes per iteration
                self.total_hash_count += 1000
                
                # Update hash rate every second
                current_time = time.time()
                if current_time - last_hash_time >= 1:
                    self.hash_rate = self.total_hash_count / (current_time - self.mining_start_time) if (current_time - self.mining_start_time) > 0 else 0
                    self._add_hash_rate_to_history(self.hash_rate)
                    last_hash_time = current_time
                
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
                        reward = self.blockchain.get_block_reward(new_block.index)
                        print(f"✅ Block #{new_block.index} mined successfully!")
                        print(f"Hash: {new_block.hash[:16]}...")
                        print(f"Mining time: {mining_time:.2f} seconds")
                        print(f"Nonce: {new_block.nonce}")
                        print(f"Reward: {reward} HayX")
                        print(f"Hash rate: {self.hash_rate:.2f} H/s")
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
                            reward = self.blockchain.get_block_reward(new_block.index)
                            print(f"✅ Empty block #{new_block.index} mined!")
                            print(f"Hash rate: {self.hash_rate:.2f} H/s")
                            print(f"Reward: {reward} HayX")
                            block_start_time = time.time()
                        else:
                            print("❌ Failed to mine empty block")
                            time.sleep(1)
                    else:
                        # Continue hashing while waiting
                        time.sleep(0.1)
                
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
        reward = self.blockchain.get_block_reward()
        if self.mining_start_time is not None:
            mining_duration = time.time() - self.mining_start_time
        else:
            mining_duration = 0
        return {
            'is_mining': self.is_mining,
            'hash_rate': self.hash_rate,
            'blocks_mined': self.blocks_mined,
            'wallet_address': self.wallet_address,
            'difficulty': self.blockchain.difficulty,
            'total_rewards': self.blocks_mined * reward,
            'last_block_time': self.last_block_time.isoformat() if self.last_block_time else None,
            'target_block_time': self.target_block_time,
            'mining_reward': reward,
            'hash_rate_history': self.hash_rate_history[-20:] if self.hash_rate_history else [],
            'total_hash_count': self.total_hash_count,
            'mining_duration': mining_duration
        }
