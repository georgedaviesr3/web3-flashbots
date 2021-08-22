import time
import os
from finalSrc.abis import swapContractABI
from eth_account.signers.local import LocalAccount
from eth_account.account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware
# Load up environ variables
ETH_ACCOUNT_FROM: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_FROM"))
ETH_ACCOUNT_TO: LocalAccount = Account.from_key(os.environ.get("ETH_PRIVATE_TO"))

#GLOBAL VARS
CONTRACT_ADDRESS = "0x21E89f008FBAf13b2Cf366bfe50258A6F5909851"
WETH = "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6"
DAI = "0xdc31Ee1784292379Fbb2964b3B9C4124D8F89C60"
CHAIN_ID = 5

# Infura node
print("Loading w3...")
w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/0f2c61d277ef4e2a84429e60760e10be'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Goerli poa middleware

fromBalance = w3.fromWei(w3.eth.get_balance(ETH_ACCOUNT_FROM.address),"ether")
toBalance = w3.fromWei(w3.eth.get_balance(ETH_ACCOUNT_TO.address), "ether")
print(f"Initial balances...\nFROM: {fromBalance} \nTO: {toBalance}")

swapContract = w3.eth.contract(address = CONTRACT_ADDRESS, abi = swapContractABI.abi)


amountToSpend = 1 * (10**18)  # 1 dai
transaction = swapContract.functions.swapMyTokens(DAI, WETH, amountToSpend).buildTransaction({
    "gasPrice": w3.toWei('40', 'gwei'),
    "gas": 2000000,
    "nonce": w3.eth.get_transaction_count(ETH_ACCOUNT_FROM.address),
    "chainId": CHAIN_ID,
})

signedTx = ETH_ACCOUNT_FROM.sign_transaction(transaction)
print(f'Created transaction {signedTx.hash.hex()}')

txn_hash = w3.eth.sendRawTransaction(signedTx.rawTransaction)

count = 0
while (count < 5):
    count += 1
    time.sleep(10)

finalFromBalance = w3.fromWei(w3.eth.get_balance(ETH_ACCOUNT_FROM.address),"ether")
finalToBalance = w3.fromWei(w3.eth.get_balance(ETH_ACCOUNT_TO.address), "ether")
print(f"Final balances...\nFROM: {finalFromBalance} \nTO: {finalToBalance}")
