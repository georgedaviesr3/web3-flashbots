from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware
from flashbots import flashbot
from flashbots.types import SignTx
from eth_account.account import Account
from web3 import Web3, HTTPProvider, exceptions
from web3.types import TxParams, Wei

import os
import environment_vars
import requests
import math

ETH_ACCOUNT_FROM: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_FROM"))
ETH_ACCOUNT_TO: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_TO"))
ETH_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(
    os.environ.get("ETH_SIGNING_KEY")
)

print("Connecting to RPC")
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/0f2c61d277ef4e2a84429e60760e10be"))
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(ETH_ACCOUNT_FROM))
flashbot(w3, ETH_ACCOUNT_SIGNATURE)

print(
    f"From account {ETH_ACCOUNT_FROM.address}: {w3.eth.get_balance(ETH_ACCOUNT_FROM.address)}"
)
print(
    f"To account {ETH_ACCOUNT_TO.address}: {w3.eth.get_balance(ETH_ACCOUNT_TO.address)}"
)

print("Creating tx and bundle...")
# create a transaction
amountToSend = w3.toWei('0.01', 'ether')  # 0.01 ether
tx: TxParams = {
    "to": ETH_ACCOUNT_TO.address,
    "value": amountToSend,
    "gasPrice": w3.toWei('4000000', 'gwei'),
    "gas": 2000000,
    "nonce": w3.eth.get_transaction_count(ETH_ACCOUNT_FROM.address),
    "chainId": 1,
}

signed_tx = ETH_ACCOUNT_FROM.sign_transaction(tx)
print(f'created transasction {signed_tx.hash.hex()}')
print(tx)

bundle = [
    {"signed_transaction": signed_tx.rawTransaction},
]
block_number = w3.eth.blockNumber

sim = w3.flashbots.simulate(bundle, block_number)
print(sim)
