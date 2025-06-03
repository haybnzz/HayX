import argparse
from hayx.crypto.wallet import Wallet

def create_wallet(name):
    wallet = Wallet(name)
    print(f"✅ Wallet created: {wallet.name}")
    print(f"📬 Address: {wallet.get_address()}")

def list_wallets():
    wallets = Wallet.list_wallets()
    if wallets:
        print("🔐 Available wallets:")
        for w in wallets:
            print(f" - {w}")
    else:
        print("⚠️ No wallets found.")

def show_wallet_info(name):
    if name not in Wallet.list_wallets():
        print(f"❌ Wallet '{name}' not found.")
        return
    wallet = Wallet(name)
    print(f"🔍 Wallet: {wallet.name}")
    print(f"📬 Address: {wallet.get_address()}")
    print(f"💰 Balance: {wallet.balance} HayX")
    print(f"📜 Transactions: {len(wallet.transactions)}")

def main():
    parser = argparse.ArgumentParser(description="HayX Wallet CLI")
    subparsers = parser.add_subparsers(dest="command")

    parser_create = subparsers.add_parser("create", help="Create a new wallet")
    parser_create.add_argument("name", help="Wallet name")

    parser_list = subparsers.add_parser("list", help="List all wallets")

    parser_info = subparsers.add_parser("info", help="Show wallet info")
    parser_info.add_argument("name", help="Wallet name")

    args = parser.parse_args()

    if args.command == "create":
        create_wallet(args.name)
    elif args.command == "list":
        list_wallets()
    elif args.command == "info":
        show_wallet_info(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
 
