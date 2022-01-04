
#!/bin/python3

from src.exploit import exploit
from src.common import from_bytes, to_bytes
from src.config import Config
from src.device import Device
from src.logger import log
from src.bruteforce import bruteforce

import argparse
import os

DEFAULT_CONFIG = "default_config.json5"
PAYLOAD_DIR = "payloads/"
DEFAULT_PAYLOAD = "generic_dump_payload.bin"
DEFAULT_DA_ADDRESS = 0x200D00


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Device config")
    parser.add_argument("-t", "--test", help="Testmode", const="0x9900", nargs='?')
    parser.add_argument("-w", "--watchdog", help="Watchdog address(in hex)")
    parser.add_argument("-u", "--uart", help="UART base address(in hex)")
    parser.add_argument("-v", "--var_1", help="var_1 value(in hex)")
    parser.add_argument("-a", "--payload_address", help="payload_address value(in hex)")
    parser.add_argument("-p", "--payload", help="Payload to use")
    parser.add_argument("-f", "--force", help="Force exploit on insecure device", action="store_true")
    parser.add_argument("-n", "--no_handshake", help="Skip handshake", action="store_true")