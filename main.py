import sys
from staff import Manager
from loguru import logger


def process_keys():
    try:
        with open('private_keys.txt', 'r') as file:
            private_keys = file.read().splitlines()
    except FileNotFoundError:
        logger.warning("File 'private_keys.txt' not found")
        sys.exit(1)

    success_keys = []
    fail_keys = []

    for key in private_keys:
        m = Manager(key)
        result = m.claim()

        if result == 1:
            success_keys.append(key)
        else:
            fail_keys.append(key)

    with open('private_keys.txt', 'w') as file:
        for key in private_keys:
            if key not in success_keys and key not in fail_keys:
                file.write(key + '\n')

    try:
        with open('success_keys.txt', 'a') as file:
            for key in success_keys:
                file.write(key + '\n')
    except FileNotFoundError:
        logger.warning("File 'success_keys.txt' not found. Creating a new file.")
        with open('success_keys.txt', 'w') as file:
            for key in success_keys:
                file.write(key + '\n')

    try:
        with open('fail_keys.txt', 'a') as file:
            for key in fail_keys:
                file.write(key + '\n')
    except FileNotFoundError:
        logger.warning("File 'fail_keys.txt' not found. Creating a new file.")
        with open('fail_keys.txt', 'w') as file:
            for key in fail_keys:
                file.write(key + '\n')


if __name__ == "__main__":
    process_keys()