import random
import sys
import time

from staff import Manager
from loguru import logger
from config import *


def gas_gate(w3):
    attempt = 0
    while True:
        try:
            gas_price = w3.eth.gas_price
            gas_price_gwei = w3.from_wei(gas_price, 'gwei')
            attempt = 0
            if gas_price_gwei <= MAX_GAS:
                logger.success(f"Gas price: {gas_price_gwei} gwei < {MAX_GAS} gwei")
                break
            else:
                logger.error(f"Gas price: {gas_price_gwei} gwei > {MAX_GAS} gwei")
                time.sleep(40)
        except Exception as e:
            attempt += 1
            if attempt == 10:
                logger.critical(f"error after {attempt} consecutive attempts"
                                f"\n{e}")
            time.sleep(1)


def process_keys():
    try:
        with open('private_keys.txt', 'r') as file:
            private_keys = file.read().splitlines()
    except FileNotFoundError:
        logger.warning("File 'private_keys.txt' not found")
        sys.exit(1)

    if SHUFFLE:
        random.shuffle(private_keys)

    success_keys, fail_keys = [], []

    for key in private_keys:
        m = Manager(key)

        gas_gate(m.w3)
        result = m.claim()

        if result == 1:
            success_keys.append(key)
        else:
            fail_keys.append(key)

        with open('success_keys.txt', 'a') as file:
            for key in set(success_keys):
                file.write(key + '\n')

        with open('fail_keys.txt', 'a') as file:
            for key in set(fail_keys):
                file.write(key + '\n')

        t = random.randint(sleep_min, sleep_max)
        logger.info(f"Process will hold for {t} seconds")
        time.sleep(t)


if __name__ == "__main__":
    process_keys()
