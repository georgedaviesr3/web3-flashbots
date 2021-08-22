import environment_vars
import time
import os
import swapContract
import transferContract
from eth_account.signers.local import LocalAccount
import IERC20
import wethABI
import erc20ABI
from web3.middleware import construct_sign_and_send_raw_middleware
import requests
from flashbots import flashbot
from flashbots.types import SignTx
from eth_account.account import Account
from web3 import Web3, HTTPProvider
from web3.types import TxParams, Wei
import requests
import math
from web3.middleware import geth_poa_middleware
# Load up environ variables
ETH_ACCOUNT_FROM: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_FROM"))
ETH_ACCOUNT_TO: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_TO"))

#GLOBAL VARS
CONTRACT_ADDRESS = "0x15303f9ABa636994D3FeED6055B02597f752D323"
WETH = "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6"
DAI = "0xdc31Ee1784292379Fbb2964b3B9C4124D8F89C60"
CHAIN_ID = 5
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

# Infura node
print("Loading w3...")
w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/0f2c61d277ef4e2a84429e60760e10be'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Goerli poa middleware

erc20Contract = w3.eth.contract(address = DAI, abi = erc20ABI.abi)

amountToApprove = w3.toWei('1', 'ether')

approveTx = erc20Contract.functions.approve(CONTRACT_ADDRESS, amountToApprove).buildTransaction({
    "gasPrice": w3.toWei('40', 'gwei'),
    "gas": 2000000,
    "nonce": w3.eth.get_transaction_count(ETH_ACCOUNT_FROM.address),
    "chainId": CHAIN_ID,
})

signedTx = ETH_ACCOUNT_FROM.sign_transaction(approveTx)
print(f'Created transaction {signedTx.hash.hex()}')

txn_hash = w3.eth.sendRawTransaction(signedTx.rawTransaction)

count = 0
while (count < 5):
    count += 1
    time.sleep(10)

print("Approved")
