# code academy tutorial deploying smart contract to goerli testnet using web3.py and infura


from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

install_solc("0.7.0")


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    # solc_version="0.7.0",
)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connecting to goerli via infura
w3 = Web3(Web3.HTTPProvider(
    "https://goerli.infura.io/v3/c84f75df56804a568df22ed1d5dd2f34"))
chain_id = 5
public_key = "0xf7A9e609cb36e4541052677fa09bB04174c6cf0f"
private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.getTransactionCount(public_key)

transaction = SimpleStorage.constructor().build_transaction(
    {"chainId": chain_id, "from": public_key, "nonce": nonce, "gasPrice": w3.eth.gas_price})

signed_tx = w3.eth.account.sign_transaction(
    transaction, private_key=private_key)

tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# when working with a contract you need: Address and ABI
# .call() is just a simulation of the contract
# .transact() attempts to make a state change
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# print(simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(15).call())
# print(simple_storage.functions.retrieve().call())


# the nonce can only be used once - we used it already to deploy tx

# create the transaction
store_transaction = simple_storage.functions.store(25).buildTransaction(
    {"chainId": chain_id, "from": public_key, "nonce": nonce+1, "gasPrice": w3.eth.gas_price})

# sign the transaction
signed_store_transaction = w3.eth.account.signTransaction(
    store_transaction, private_key=private_key)

# send the transaction
send_store_tx = w3.eth.send_raw_transaction(
    signed_store_transaction.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print(simple_storage.functions.retrieve().call())
