import json
import random

import requests
from web3 import Web3, HTTPProvider
from eth_account import Account
from loguru import logger

gas_lim_min, gas_lim_max = 85000, 100000


class Manager:
    def __init__(self, key):
        self.private_key = key
        self.w3 = Web3(HTTPProvider('https://eth.llamarpc.com'))
        self.account = Account.from_key(key)
        self.address = self.account.address

    def get_eth_address_data(self):
        address = self.address.lower()
        addr_prefix = address[2:5]
        url = f"https://pub-88646eee386a4ddb840cfb05e7a8d8a5.r2.dev/eth_data/{addr_prefix}.json"

        try:
            response = requests.get(url)
            data = response.json()
            data_lower = {k.lower(): v for k, v in data.items()}

            if address in data_lower:
                address_data = data_lower[address]
                wei_amount = int(address_data['amount'], 16)
                if wei_amount is None:
                    return None, None, None
                index = address_data['index']
                proof = address_data['proof']
                return wei_amount, index, proof
            else:
                return None, None, None
        except Exception as e:
            logger.critical(f"An error occurred: {e}")
            return None, None, None

    def _submit_and_log_transaction(self, txn):
        try:
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
            txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=120)
            if receipt['status'] == 1:
                logger.success(f"Txn completed: https://etherscan.io/tx/{txn_hash.hex()}")
                return 1
            else:
                logger.warning(f"Txn unsuccessful: https://etherscan.io/tx/{txn_hash.hex()}")
                return 0
        except Exception as e:
            logger.critical(f"Error while making txn for wallet {self.address}: \n{e}")
            return 0

    def claim(self):
        wei_amount, index, proof = self.get_eth_address_data()
        try:
            contract_address = self.w3.to_checksum_address('0x9234f83473C03be04358afC3497d6293B2203288')
            with open('claim.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(gas_lim_min, gas_lim_max)
            base_fee = self.w3.eth.fee_history(1, 'latest')['baseFeePerGas'][-1]
            max_priority_fee = int(self.w3.to_wei(0.5, 'gwei'))
            max_fee = base_fee + int(self.w3.to_wei(1.5, 'gwei'))

            txn = contract.functions.claim(index, self.address, wei_amount, proof).build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': max_priority_fee,
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })
            logger.info(f"Address {self.address} is about to claim {wei_amount / 10 ** 18} ZK tokens")
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0


if __name__ == "__main__":
    key = ''
    m = Manager(key)
    m.claim()
