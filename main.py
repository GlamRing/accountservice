
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
    parser.add_argument("-m", "--crash_method", help="Method to use for crashing preloader (0, 1, 2)", type=int)
    parser.add_argument("-k", "--kamakiri", help="Force use of kamakiri", action="store_true")
    arguments = parser.parse_args()

    if arguments.config:
        if not os.path.exists(arguments.config):
            raise RuntimeError("Config file {} doesn't exist".format(arguments.config))
    elif not os.path.exists(DEFAULT_CONFIG):
        raise RuntimeError("Default config is missing")

    device = Device().find()

    config, serial_link_authorization, download_agent_authorization, hw_code  = get_device_info(device, arguments)

    while device.preloader:
        device = crash_preloader(device, config)
        config, serial_link_authorization, download_agent_authorization, hw_code  = get_device_info(device, arguments)

    log("Disabling watchdog timer")
    device.write32(config.watchdog_address, 0x22000064)

    if device.libusb0:
        arguments.kamakiri = True

    bootrom__name = "bootrom_" + hex(hw_code)[2:] + ".bin"

    if arguments.test and not arguments.kamakiri:
        dump_ptr = int(arguments.test, 16)
        found = False
        while not found:
            log("Test mode, testing " + hex(dump_ptr) + "...")
            found, dump_ptr = bruteforce(device, config, dump_ptr)
            device.dev.close()
            reconnect_message()
            device = Device().find(wait=True)
            device.handshake()
            while device.preloader:
                device = crash_preloader(device, config)
                device.handshake()
        log("Found " + hex(dump_ptr) + ", dumping bootrom to {}".format(bootrom__name))
        open(bootrom__name, "wb").write(bruteforce(device, config, dump_ptr, True))
        exit(0)

    if serial_link_authorization or download_agent_authorization or arguments.force:
        log("Disabling protection")

        payload = prepare_payload(config)

        result = exploit(device, config, payload, arguments)
        if arguments.test:
            while not result:
                device.dev.close()
                config.var_1 += 1
                log("Test mode, testing " + hex(config.var_1) + "...")
                reconnect_message()
                device = Device().find(wait=True)
                device.handshake()
                while device.preloader:
                    device = crash_preloader(device, config)
                    device.handshake()
                result = exploit(device, config, payload, arguments)