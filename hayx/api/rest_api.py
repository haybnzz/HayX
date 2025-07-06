from flask import Blueprint, request, jsonify
from hayx.blockchain.blockchain import Blockchain
from hayx.blockchain.transaction import Transaction
from hayx.crypto.wallet import Wallet
from hayx.mining.miner import Miner
from hayx.network.node import Node
from config import Config
import time

api = Blueprint('api', __name__)
blockchain = Blockchain()

# Proper wallet initialization
wallets = Wallet.list_wallets()
wallet_name = wallets[0] if wallets else "default"
wallet = Wallet(wallet_name)

miner = Miner(wallet.get_address())
node = Node(blockchain)


@api.route('/wallet/create', methods=['POST'])
def create_wallet():
    name = request.json.get('name', f'wallet_{int(time.time())}')
    new_wallet = Wallet(name)
    return jsonify({'status': 'success', 'address': new_wallet.get_address()})


@api.route('/wallet/switch', methods=['POST'])
def switch_wallet():
    global wallet, miner
    name = request.json.get('name')
    if name in Wallet.list_wallets():
        wallet = Wallet(name)
        miner = Miner(wallet.get_address())
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Wallet not found'})


@api.route('/transaction/send', methods=['POST'])
def send_transaction():
    data = request.json
    recipient = data.get('recipient')
    amount = float(data.get('amount'))
    fee = float(data.get('fee', 0.01))

    if not wallet:
        return jsonify({'status': 'error', 'message': 'No wallet selected'})

    balance = blockchain.get_balance(wallet.get_address())
    if balance < amount + fee:
        return jsonify({'status': 'error', 'message': 'Insufficient balance'})

    tx = Transaction(wallet.get_address(), recipient, amount, fee)
    tx.sign_transaction(wallet.keypair.get_private_key_hex())

    if blockchain.add_transaction(tx):
        return jsonify({'status': 'success', 'tx_id': tx.tx_id})
    return jsonify({'status': 'error', 'message': 'Transaction failed'})


@api.route('/mining/start', methods=['POST'])
def start_mining():
    miner.start_mining()
    return jsonify({'status': 'success'})


@api.route('/mining/stop', methods=['POST'])
def stop_mining():
    miner.stop_mining()
    return jsonify({'status': 'success'})


@api.route('/node/start', methods=['POST'])
def start_node():
    node.start()
    return jsonify({'status': 'success'})


@api.route('/node/stop', methods=['POST'])
def stop_node():
    node.stop()
    return jsonify({'status': 'success'})


@api.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'blockchain': blockchain.get_stats(),
        'wallet': {
            'address': wallet.get_address(),
            'balance': blockchain.get_balance(wallet.get_address())
        },
        'mining': miner.get_mining_stats(),
        'node': {
            'is_running': node.is_running,
            'peer_count': len(node.get_peers())
        }
    })
