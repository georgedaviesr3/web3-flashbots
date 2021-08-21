import os
import environment_vars

from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware
from flashbots import flashbot
from flashbots.types import SignTx
from eth_account.account import Account
from web3 import Web3, HTTPProvider, exceptions
from web3.types import TxParams, Wei

# Initialise accounts from environment vars
# Signature account is only used for identification to allow me to build a reputation with FB
ETH_ACCOUNT_FROM: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_FROM"))
ETH_ACCOUNT_TO: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_TO"))
ETH_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(os.environ.get("ETH_SIGNATURE_KEY"))

# GLOBAL VARIABLES
CHAIN_ID = 5

# Connect to Goerli Infura node
# Insert proof-of-authority middleware for Goerli
# Connect to FB relay (FBs Goerli HTTP provider URI set in environ vars to "https://relay-goerli.flashbots.net/")
def initialise():
    print("Connecting to RPC...")
    w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/0f2c61d277ef4e2a84429e60760e10be"))

    w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Goerli poa middleware
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(ETH_ACCOUNT_FROM))
    flashbot(w3, ETH_ACCOUNT_SIGNATURE,56656)  # FB middleware

    print(f"From account {ETH_ACCOUNT_FROM.address}: {w3.eth.get_balance(ETH_ACCOUNT_FROM.address)}")
    print(f"To account {ETH_ACCOUNT_TO.address}: {w3.eth.get_balance(ETH_ACCOUNT_TO.address)}")

    return w3

def buildAndSignTx(value = '0.01', gasPrice = '50', gas = 2000000):
    print("Building tx...")
    tx: TxParams = {
        "to": ETH_ACCOUNT_TO.address,
        "value": w3.toWei(value, 'ether'),
        "gasPrice": w3.toWei(gasPrice, 'gwei'),
        "gas": gas,
        "nonce": w3.eth.get_transaction_count(ETH_ACCOUNT_FROM.address),
        "chainId": CHAIN_ID,
    }
    signedTx = ETH_ACCOUNT_FROM.sign_transaction(tx)
    print(f'Created transaction {signedTx.hash.hex()}')

    return signedTx

w3 = initialise()

signedTx = buildAndSignTx()

# Bundle tx for FB
bundle = [
    {"signed_transaction": signedTx.rawTransaction},
]

blockNumber = w3.eth.blockNumber

# Simulate tx to ensure it's valid
#sim = w3.flashbots.simulate(bundle, blockNumber + 1)
#print(sim)

# Send FB bundle to relay
# Target the next 9 blocks as FB only runs a few Goerli validators
for i in range(1, 10):
    print(f"Sending bundle to block {blockNumber + i}...")
    w3.flashbots.send_bundle(bundle, target_block_number=blockNumber + i)
print(f'bundle broadcast at block {blockNumber}')

tx_id = signedTx.hash
while True:
    try:
        w3.eth.waitForTransactionReceipt(tx_id, timeout=1, poll_latency=0.1)
        break

    except exceptions.TimeExhausted:
        if w3.eth.block_number >= (blockNumber + 10):
            print("ERROR: transaction was not mined")
            exit(1)

print(f'transaction confirmed at block {w3.eth.block_number}: {tx_id.hex()}')