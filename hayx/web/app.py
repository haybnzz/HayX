from flask import Flask, render_template, redirect, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime, timedelta
from hayx.blockchain.blockchain import Blockchain
from hayx.crypto.wallet import Wallet
from hayx.mining.miner import Miner
from hayx.network.node import Node
from hayx.api.rest_api import api
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hayx_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Register REST API Blueprint
app.register_blueprint(api, url_prefix='/api')

# Global instances
blockchain = Blockchain()
current_wallet = None
current_miner = None
node = None

# Helper: Load/Create Wallet
def init_default_wallet():
    global current_wallet
    wallets = Wallet.list_wallets()
    if wallets:
        try:
            current_wallet = Wallet(wallets[0])
            print(f"Loaded wallet: {wallets[0]}")
        except Exception as e:
            print(f"⚠️ Failed to load wallet {wallets[0]}: {e}")
            current_wallet = None
    else:
        print("⚠️ No wallets found.")
        current_wallet = None

init_default_wallet()

# Custom Jinja2 filter for timestamp_to_date
def timestamp_to_date(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError):
        return "Unknown Date"

app.jinja_env.filters['timestamp_to_date'] = timestamp_to_date

# Custom error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    print(f"⚠️ 500 Error: {str(error)}")
    return render_template('error.html', error_message="An unexpected error occurred. Please check server logs or try again."), 500

# Routes
@app.route('/')
def home():
    return redirect('/wallet')

@app.route('/wallet')
def wallet():
    global current_wallet
    wallets = Wallet.list_wallets()
    balance = 0
    transactions = []

    if not current_wallet and wallets:
        try:
            current_wallet = Wallet(wallets[0])
            print(f"✅ Loaded default wallet: {current_wallet.name}")
        except Exception as e:
            print(f"⚠️ Failed to load default wallet: {e}")
            current_wallet = None

    if current_wallet:
        try:
            balance = blockchain.get_balance(current_wallet.get_address())
            transactions = blockchain.get_transaction_history(current_wallet.get_address())
        except Exception as e:
            print(f"⚠️ Failed to fetch wallet data: {e}")
            balance = 0
            transactions = []

    return render_template("wallet.html",
                           wallet=current_wallet,
                           balance=balance,
                           transactions=transactions,
                           wallets=wallets)
@app.route('/miner')
def miner():
    global current_wallet, current_miner

    if not current_wallet:
        return render_template('error.html', error_message="No wallet loaded. Please create or switch a wallet first."), 500

    if not current_miner:
        current_miner = Miner(current_wallet.get_address())

    mining_stats = current_miner.get_mining_stats() if current_miner else {
        'is_mining': False,
        'hash_rate': 0,
        'blocks_mined': 0,
        'wallet_address': '',
        'difficulty': blockchain.difficulty
    }

    return render_template('miner.html', mining_stats=mining_stats)


@app.route('/chain')
def chain():
    blocks = [block.to_dict() for block in reversed(blockchain.chain[-10:])]
    stats = blockchain.get_stats()
    return render_template('chain.html', blocks=blocks, stats=stats)

@app.route('/node')
def node_page():
    peers = node.get_peers() if node else []
    node_stats = {
        'is_running': node.is_running if node else False,
        'peer_count': len(peers),
        'port': Config.P2P_PORT
    }
    return render_template('node.html', node_stats=node_stats, peers=peers)

@app.route('/settings')
def settings():
    return render_template('settings.html', config=Config)

# API Endpoints
@app.route('/api/mining/start', methods=['POST'])
def start_mining():
    global current_miner, current_wallet
    try:
        if not current_wallet:
            return jsonify({'status': 'error', 'message': 'No wallet loaded'}), 400
        
        if not current_miner:
            current_miner = Miner(current_wallet.get_address())
        
        if not current_miner.is_mining:
            current_miner.start_mining()
            print(f"✅ Mining started for wallet: {current_wallet.name}")
            return jsonify({'status': 'success', 'message': 'Mining started successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Mining is already active'}), 400
            
    except Exception as e:
        print(f"❌ Error starting mining: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/mining/stop', methods=['POST'])
def stop_mining():
    global current_miner
    try:
        if current_miner and current_miner.is_mining:
            current_miner.stop_mining()
            print("✅ Mining stopped")
            return jsonify({'status': 'success', 'message': 'Mining stopped successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Mining is not active'}), 400
            
    except Exception as e:
        print(f"❌ Error stopping mining: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/mining/stats')
def get_mining_stats_api():
    global current_miner, current_wallet, blockchain
    try:
        if not current_wallet:
            return jsonify({'error': 'No wallet loaded'}), 400
        
        if not current_miner:
            current_miner = Miner(current_wallet.get_address())
        
        stats = current_miner.get_mining_stats() if current_miner else {}
        wallet_balance = blockchain.get_balance(current_wallet.get_address()) if current_wallet else 0
        
        return jsonify({
            'hash_rate': stats.get('hash_rate', 0),
            'blocks_mined': stats.get('blocks_mined', 0),
            'total_rewards': stats.get('blocks_mined', 0) * 50,
            'is_mining': stats.get('is_mining', False),
            'difficulty': blockchain.difficulty if hasattr(blockchain, 'difficulty') else 1,
            'pending_transactions': len(blockchain.pending_transactions) if hasattr(blockchain, 'pending_transactions') else 0,
            'wallet_balance': wallet_balance,
            'wallet_address': current_wallet.get_address(),
            'timestamp': time.time()
        })
    except Exception as e:
        print(f"❌ Error getting mining stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mining/hashrate-history')
def get_hashrate_history():
    global current_miner
    if not current_miner:
        return jsonify({'error': 'No active miner'}), 400
    
    history = getattr(current_miner, 'hash_rate_history', [])
    if not history:
        current_hash_rate = current_miner.get_mining_stats().get('hash_rate', 0)
        now = datetime.now()
        history = []
        for i in range(20):
            timestamp = now - timedelta(minutes=i)
            variation = current_hash_rate * 0.1 * (0.5 - abs(i % 10 - 5) / 10)
            hash_rate = max(0, current_hash_rate + variation)
            history.append({
                'timestamp': timestamp.isoformat(),
                'hash_rate': round(hash_rate, 2)
            })
        history.reverse()
    
    return jsonify(history)

@app.route('/api/mining/pending-transactions')
def get_pending_transactions():
    pending_txs = []
    if hasattr(blockchain, 'pending_transactions'):
        for tx in blockchain.pending_transactions[:10]:
            pending_txs.append({
                'from_address': tx.from_address if hasattr(tx, 'from_address') else 'N/A',
                'to_address': tx.to_address if hasattr(tx, 'to_address') else 'N/A',
                'amount': tx.amount if hasattr(tx, 'amount') else 0,
                'timestamp': getattr(tx, 'timestamp', time.time())
            })
    return jsonify(pending_txs)

@app.route('/wallet/switch', methods=['POST'])
def switch_wallet_route():
    global current_wallet, current_miner
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'status': 'error', 'message': 'Missing wallet name'}), 400

        name = data.get('name')
        if not name:
            return jsonify({'status': 'error', 'message': 'Wallet name cannot be empty'}), 400

        if name not in Wallet.list_wallets():
            return jsonify({'status': 'error', 'message': f'Wallet {name} not found'}), 404

        try:
            current_wallet = Wallet(name)
        except ValueError as e:
            print(f"❌ Failed to load wallet {name}: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

        if current_miner:
            try:
                current_miner.stop_mining()
                current_miner = Miner(current_wallet.get_address())
            except Exception as e:
                print(f"❌ Failed to update miner: {e}")
                return jsonify({'status': 'error', 'message': f'Failed to update miner: {str(e)}'}), 500

        print(f"✅ Wallet switched to: {current_wallet.name}")
        return jsonify({
            'status': 'success',
            'message': f'Switched to wallet: {name}',
            'wallet': {
                'name': current_wallet.name,
                'address': current_wallet.get_address(),
                'balance': blockchain.get_balance(current_wallet.get_address())
            }
        })

    except Exception as e:
        print(f"❌ Wallet switch failed: {e}")
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

# Helper Functions
def calculate_estimated_block_time(hash_rate):
    if hash_rate <= 0:
        return "∞"
    difficulty = blockchain.difficulty if hasattr(blockchain, 'difficulty') else 1
    estimated_seconds = (difficulty * 1000000) / hash_rate
    if estimated_seconds < 60:
        return f"{estimated_seconds:.1f}s"
    elif estimated_seconds < 3600:
        return f"{estimated_seconds/60:.1f}m"
    else:
        return f"{estimated_seconds/3600:.1f}h"

def calculate_mining_efficiency(hash_rate, difficulty):
    if difficulty <= 0:
        return 100
    base_efficiency = (hash_rate / (difficulty * 1000)) * 100
    return min(100, max(0, base_efficiency))

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'message': 'Connected to HayX'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Periodic Background Updates
def background_updates():
    while True:
        try:
            socketio.sleep(2)  # Update every 2 seconds for better real-time experience
            
            # Get current stats
            blockchain_stats = blockchain.get_stats()
            mining_stats = current_miner.get_mining_stats() if current_miner else {'is_mining': False}
            wallet_balance = 0
            wallet_address = ''
            
            if current_wallet:
                try:
                    wallet_balance = blockchain.get_balance(current_wallet.get_address())
                    wallet_address = current_wallet.get_address()
                except Exception as e:
                    print(f"⚠️ Error getting wallet balance: {e}")
            
            # Get node stats
            node_stats = {
                'is_running': node.is_running if node else False,
                'peer_count': len(node.get_peers()) if node else 0
            }
            
            stats = {
                'blockchain': blockchain_stats,
                'mining': mining_stats,
                'wallet': {
                    'address': wallet_address,
                    'balance': wallet_balance
                },
                'node': node_stats,
                'timestamp': time.time()
            }
            
            socketio.emit('stats_update', stats)
            
        except Exception as e:
            print(f"⚠️ Error in background updates: {e}")
            socketio.sleep(5)  # Wait longer on error

socketio.start_background_task(background_updates)

# Run the App
if __name__ == '__main__':
    socketio.run(app, debug=True)
