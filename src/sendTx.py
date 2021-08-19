import environment_vars
import time
import os

from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from flashbots import flashbot
from flashbots.types import SignTx
from eth_account.account import Account
from web3 import Web3, HTTPProvider
from web3.types import TxParams, Wei

# Load up environ variables
ETH_ACCOUNT_FROM: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_FROM"))
ETH_ACCOUNT_TO: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_TO"))

# Infura node
w3  = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/0f2c61d277ef4e2a84429e60760e10be'))
fromBalance = w3.fromWei(w3.eth.get_balance(ETH_ACCOUNT_FROM.address),"ether")
toBalance = w3.fromWei(w3.eth.get_balance(ETH_ACCOUNT_TO.address), "ether")
print("w3 loaded...")
print(f"Initial balances...\nFROM: {fromBalance} \nTO: {toBalance}")

print(w3.toWei(toBalance, "wei"))

# Build tx
amountToSend = w3.toWei('0.01', 'ether')  # 0.01 ether
transaction = {
    'to': ETH_ACCOUNT_TO.address,
    'value': amountToSend,
    'gas': 2000000,
    'gasPrice': w3.toWei('40', 'gwei'),
    'nonce': w3.eth.get_transaction_count(ETH_ACCOUNT_FROM.address),
    'chainId': 5
}

signed_txn = w3.eth.account.sign_transaction(transaction, os.environ.get("ETH_PRIVATE_FROM"))

txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
count = 0
while (count < 5):
    count += 1
    time.sleep(10)

finalFromBalance = w3.fromWei(w3.eth.get_balance(ETH_ACCOUNT_FROM.address),"ether")
finalToBalance = w3.fromWei(w3.eth.get_balance(ETH_ACCOUNT_TO.address), "ether")
print(f"Final balances...\nFROM: {finalFromBalance} \nTO: {finalToBalance}")