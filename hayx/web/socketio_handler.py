from flask_socketio import emit
from hayx.blockchain.blockchain import Blockchain
from hayx.mining.miner import Miner
from hayx.crypto.wallet import Wallet
from hayx.network.node import Node

blockchain = Blockchain()
current_wallet = None
current_miner = None
node = None

def init(wallet_name=None):
    global current_wallet, current_miner, node

    wallets = Wallet.list_wallets()
    if wallet_name and wallet_name in wallets:
        current_wallet = Wallet(wallet_name)
    elif wallets:
        current_wallet = Wallet(wallets[0])
    else:
        current_wallet = Wallet("default")

    current_miner = Miner(current_wallet.get_address())
    node = Node(blockchain)

def register_socketio_events(socketio):

    @socketio.on('connect')
    def handle_connect():
        emit('status', {'message': '🔌 Connected to HayX Node'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('🔌 Client disconnected')

    @socketio.on('get_stats')
    def handle_get_stats():
        emit('stats_update', get_stats())

    @socketio.on('start_mining')
    def handle_start_mining():
        if current_miner:
            current_miner.start_mining()
            emit('status', {'message': '⛏️ Mining started'})

    @socketio.on('stop_mining')
    def handle_stop_mining():
        if current_miner:
            current_miner.stop_mining()
            emit('status', {'message': '🛑 Mining stopped'})

    @socketio.on('send_transaction')
    def handle_send_transaction(data):
        from hayx.blockchain.transaction import Transaction
        recipient = data.get('recipient')
        amount = float(data.get('amount', 0))
        fee = float(data.get('fee', 0.01))

        if not recipient or amount <= 0:
            emit('error', {'message': 'Invalid transaction data'})
            return

        tx = Transaction(current_wallet.get_address(), recipient, amount, fee)
        tx.sign_transaction(current_wallet.keypair.get_private_key_hex())

        if blockchain.add_transaction(tx):
            emit('status', {'message': '✅ Transaction added'})
        else:
            emit('error', {'message': '❌ Transaction failed'})

    @socketio.on('get_chain')
    def handle_get_chain():
        chain_data = [block.to_dict() for block in blockchain.chain]
        emit('chain_data', {'chain': chain_data})

def get_stats():
    return {
        'blockchain': blockchain.get_stats(),
        'wallet': {
            'address': current_wallet.get_address() if current_wallet else '',
            'balance': blockchain.get_balance(current_wallet.get_address()) if current_wallet else 0
        },
        'mining': current_miner.get_mining_stats() if current_miner else {'is_mining': False},
        'node': {
            'is_running': node.is_running if node else False,
            'peer_count': len(node.get_peers()) if node else 0
        }
    }
