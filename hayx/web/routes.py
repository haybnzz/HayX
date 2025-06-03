from flask import render_template, request, jsonify
from hayx.crypto.wallet import Wallet
from hayx.blockchain.blockchain import Blockchain
from hayx.mining.miner import Miner
from hayx.network.node import Node
from config import Config

# Shared instances (usually you’d inject or import these from a common state manager)
blockchain = Blockchain()
current_wallet = Wallet.list_wallets()[0] if Wallet.list_wallets() else Wallet("default")
current_miner = Miner(current_wallet.get_address())
node = Node(blockchain)

def register_routes(app):
    @app.route('/wallet')
    def wallet():
        balance = blockchain.get_balance(current_wallet.get_address())
        transactions = blockchain.get_transaction_history(current_wallet.get_address())
        wallets = Wallet.list_wallets()
        return render_template('wallet.html',
                               wallet=current_wallet,
                               balance=balance,
                               transactions=transactions,
                               wallets=wallets)

    @app.route('/miner')
    def miner():
        stats = current_miner.get_mining_stats()
        return render_template('miner.html', mining_stats=stats)

    @app.route('/chain')
    def chain():
        blocks = [block.to_dict() for block in reversed(blockchain.chain[-10:])]
        stats = blockchain.get_stats()
        return render_template('chain.html', blocks=blocks, stats=stats)

    @app.route('/node')
    def node_page():
        peers = node.get_peers() if node else []
        return render_template('node.html', node_stats={
            'is_running': node.is_running,
            'peer_count': len(peers),
            'port': Config.P2P_PORT
        }, peers=peers)

    @app.route('/settings')
    def settings():
        return render_template('settings.html', config=Config)
