# traceability/utils.py

import json
from web3 import Web3, HTTPProvider

# ------------------ Blockchain Config ------------------ #
BLOCKCHAIN_ADDRESS = "http://127.0.0.1:9545"
COMPILED_CONTRACT_PATH = "Drug.json"
DEPLOYED_CONTRACT_ADDRESS = "0x1DD4fb45C1cdC8C3f32cbaA60464c8107D4D4058"


def get_contract():
    """Return Web3 instance and contract."""
    web3 = Web3(HTTPProvider(BLOCKCHAIN_ADDRESS))
    web3.eth.defaultAccount = web3.eth.accounts[0]

    with open(COMPILED_CONTRACT_PATH) as file:
        contract_json = json.load(file)
        contract_abi = contract_json["abi"]

    contract = web3.eth.contract(address=DEPLOYED_CONTRACT_ADDRESS, abi=contract_abi)
    return web3, contract


def read_details(contract_type):
    """Read details from blockchain."""
    web3, contract = get_contract()
    if contract_type == "signup":
        return contract.functions.getUser().call()
    elif contract_type == "addproduct":
        return contract.functions.getTracingData().call()
    return ""


def save_data_blockchain(current_data, contract_type):
    """Save new data to blockchain."""
    web3, contract = get_contract()
    details = read_details(contract_type)

    if contract_type == "signup":
        details += current_data
        tx_hash = contract.functions.addUser(details).transact()
    elif contract_type == "addproduct":
        details += current_data
        tx_hash = contract.functions.setTracingData(details).transact()

    web3.eth.wait_for_transaction_receipt(tx_hash)


def update_quantity_block(current_data):
    """Update existing blockchain data."""
    web3, contract = get_contract()
    tx_hash = contract.functions.setTracingData(current_data).transact()
    web3.eth.wait_for_transaction_receipt(tx_hash)
