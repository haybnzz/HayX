#!/usr/bin/env python3
"""
Test script for HayX mining functionality
"""

import time
import requests
import json
from hayx.blockchain.blockchain import Blockchain
from hayx.crypto.wallet import Wallet
from hayx.mining.miner import Miner

def test_mining_functionality():
    """Test the mining functionality"""
    print("🧪 Testing HayX Mining Functionality")
    print("=" * 50)
    
    # Initialize components
    try:
        blockchain = Blockchain()
        print("✅ Blockchain initialized")
        
        # Create or load wallet
        wallets = Wallet.list_wallets()
        if not wallets:
            wallet = Wallet("test_wallet")
            print("✅ Created test wallet")
        else:
            wallet = Wallet(wallets[0])
            print(f"✅ Loaded wallet: {wallet.name}")
        
        # Initialize miner
        miner = Miner(wallet.get_address())
        print(f"✅ Miner initialized for address: {wallet.get_address()}")
        
        # Test mining stats
        stats = miner.get_mining_stats()
        print(f"✅ Mining stats: {stats}")
        
        # Test blockchain stats
        blockchain_stats = blockchain.get_stats()
        print(f"✅ Blockchain stats: {blockchain_stats}")
        
        # Test wallet balance
        balance = blockchain.get_balance(wallet.get_address())
        print(f"✅ Wallet balance: {balance} HayX")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_web_api():
    """Test the web API endpoints"""
    print("\n🌐 Testing Web API")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test mining stats endpoint
        response = requests.get(f"{base_url}/api/mining/stats")
        if response.status_code == 200:
            print("✅ Mining stats endpoint working")
        else:
            print(f"❌ Mining stats endpoint failed: {response.status_code}")
        
        # Test node status endpoint
        response = requests.get(f"{base_url}/api/node/status")
        if response.status_code == 200:
            print("✅ Node status endpoint working")
        else:
            print(f"❌ Node status endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Web server not running. Start with: python run.py")
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    print("🚀 HayX Mining Test Suite")
    print("=" * 50)
    
    # Test core functionality
    core_ok = test_mining_functionality()
    
    # Test web API
    test_web_api()
    
    if core_ok:
        print("\n✅ All core functionality tests passed!")
        print("\n📋 Next steps:")
        print("1. Start the web server: python run.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Go to the Miner page to start mining")
        print("4. Check the Wallet page for real-time balance updates")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.") 