from web3 import Web3
from eth_account import Account
import requests
from datetime import datetime

# ----------------------------------------
# Wallet - Mnemonic Seed Phrase (Unsafe for production)
# ----------------------------------------
SEED_PHRASE = "physical job output brass master ensure equal snap east armed hip thumb"

# ----------------------------------------
# Network Configuration
# ----------------------------------------
RPC_URL = "https://sepolia.infura.io/v3/af1fac50179e49c49a7a9da39d4315b2"
RECEIVER_ADDRESS = "0xCD6b335939B90Fd85b3B4Eb6B186c804e88E6bF9"  # destination address

# ----------------------------------------
# Initialize Wallet
# ----------------------------------------
Account.enable_unaudited_hdwallet_features()
wallet = Account.from_mnemonic(SEED_PHRASE)
PRIVATE_KEY = wallet.key
SENDER_ADDRESS = wallet.address

# ----------------------------------------
# Fetch Current ETH Price in USD
# ----------------------------------------
def get_eth_usd_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "ethereum", "vs_currencies": "usd"}
        response = requests.get(url, params=params, timeout=10).json()
        return float(response["ethereum"]["usd"])
    except Exception as e:
        print("Failed to fetch ETH price:", e)
        return None

# ----------------------------------------
# Convert USD amount to ETH
# ----------------------------------------
def get_eth_amount_for_usd(usd_amount):
    eth_price = get_eth_usd_price()
    if eth_price:
        return usd_amount / eth_price
    else:
        raise Exception("Unable to fetch ETH price.")

# ----------------------------------------
# Send ETH Transaction
# ----------------------------------------
def send_eth():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Web3 connection failed.")
        return

    try:
        eth_amount = get_eth_amount_for_usd(10)
        value = w3.to_wei(eth_amount, 'ether')
        gas_price = w3.eth.gas_price
        nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)
        chain_id = w3.eth.chain_id

        txn = {
            'to': RECEIVER_ADDRESS,
            'value': value,
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': chain_id
        }

        signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        print(f"Sent 100 USD worth of ETH (~{eth_amount:.6f} ETH)")
        print(f"Transaction Hash: {w3.to_hex(tx_hash)} at {datetime.now()}")

    except Exception as e:
        print("Transaction failed:", e)

# ----------------------------------------
# Execute Script
# ----------------------------------------
if __name__ == "__main__":
    send_eth()
