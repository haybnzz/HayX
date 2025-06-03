import argparse
import time
from hayx.mining.miner import Miner
from hayx.crypto.wallet import Wallet

def start_mining(wallet_name):
    if wallet_name not in Wallet.list_wallets():
        print(f"❌ Wallet '{wallet_name}' not found.")
        return

    wallet = Wallet(wallet_name)
    miner = Miner(wallet.get_address())

    print(f"⛏️ Starting mining with wallet '{wallet_name}'...")
    miner.start_mining()

    try:
        while True:
            stats = miner.get_mining_stats()
            print(f"🟢 Hashrate: {stats['hash_rate']:.2f} H/s | Blocks: {stats['blocks_mined']}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Stopping miner...")
        miner.stop_mining()

def main():
    parser = argparse.ArgumentParser(description="HayX Miner CLI")
    parser.add_argument("wallet", help="Wallet name to mine with")
    args = parser.parse_args()

    start_mining(args.wallet)

if __name__ == "__main__":
    main()
