import os
import json
from .block import Block
from .transaction import Transaction
from config import Config

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.mining_reward = Config.MINING_REWARD
        self.difficulty = Config.DIFFICULTY_TARGET
        self.blockchain_file = Config.BLOCKCHAIN_FILE

        self.load_or_create_genesis()

    def load_or_create_genesis(self):
        """Load blockchain from file or create genesis block."""
        if os.path.exists(self.blockchain_file):
            self.load_blockchain()
        else:
            self.create_genesis_block()
            self.save_blockchain()

    def create_genesis_block(self):
        """Create the genesis block."""
        genesis_tx = Transaction("coinbase", "genesis", Config.GENESIS_REWARD, 0)
        genesis_block = Block(0, [genesis_tx], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain = [genesis_block]

    def load_blockchain(self):
        """Load blockchain from file, handling old/new formats and corrupt data."""
        try:
            with open(self.blockchain_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    raise ValueError("Empty file")

                data = json.loads(content)

            # Old format: plain list of blocks
            if isinstance(data, list):
                print("⚠️ Detected old blockchain format. Converting…")
                self.chain = [Block.from_dict(b) for b in data]
                self.pending_transactions = []
                self.difficulty = Config.DIFFICULTY_TARGET

            # New format: dict with chain, pending_transactions, difficulty
            else:
                self.chain = [Block.from_dict(b) for b in data['chain']]
                self.pending_transactions = [
                    Transaction.from_dict(tx) for tx in data.get('pending_transactions', [])
                ]
                self.difficulty = data.get('difficulty', Config.DIFFICULTY_TARGET)

            print(f"✅ Loaded blockchain ({len(self.chain)} blocks)")

        except Exception as e:
            print(f"⚠️ Failed to load blockchain: {e}")
            print("🔄 Reinitializing with genesis block…")
            self.chain = []
            self.pending_transactions = []
            self.create_genesis_block()
            self.save_blockchain()

    def save_blockchain(self):
        """Save blockchain to file in new format."""
        payload = {
            'chain': [b.to_dict() for b in self.chain],
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'difficulty': self.difficulty
        }
        with open(self.blockchain_file, 'w') as f:
            json.dump(payload, f, indent=2)

    def get_latest_block(self):
        return self.chain[-1] if self.chain else None

    def add_transaction(self, transaction):
        if self.is_valid_transaction(transaction):
            self.pending_transactions.append(transaction)
            return True
        return False

    def is_valid_transaction(self, transaction):
        if transaction.sender == "coinbase":
            return True
        return self.get_balance(transaction.sender) >= (transaction.amount + transaction.fee)

    def mine_pending_transactions(self, mining_reward_address):
        reward_tx = Transaction("coinbase", mining_reward_address, self.mining_reward, 0)
        txs = self.pending_transactions[:Config.MAX_TRANSACTIONS_PER_BLOCK - 1]
        txs.append(reward_tx)

        new_block = Block(len(self.chain), txs, self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = self.pending_transactions[Config.MAX_TRANSACTIONS_PER_BLOCK - 1:]
        self.save_blockchain()
        return new_block

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address and tx.sender != "coinbase":
                    balance -= (tx.amount + tx.fee)
                if tx.recipient == address:
                    balance += tx.amount
        return balance

    def get_transaction_history(self, address):
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address or tx.recipient == address:
                    data = tx.to_dict()
                    data.update(block_index=block.index, block_hash=block.hash)
                    history.append(data)
        return history

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr, prev = self.chain[i], self.chain[i-1]
            if not curr.is_valid(prev) or curr.previous_hash != prev.hash:
                return False
        return True

    def get_stats(self):
        return {
            'total_blocks': len(self.chain),
            'pending_transactions': len(self.pending_transactions),
            'difficulty': self.difficulty,
            'latest_block_hash': self.get_latest_block().hash if self.chain else None,
            'total_supply': sum(self.get_balance(addr) for addr in self.get_all_addresses())
        }

    def get_all_addresses(self):
        addresses = set()
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender != "coinbase":
                    addresses.add(tx.sender)
                addresses.add(tx.recipient)
        return list(addresses)
