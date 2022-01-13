from src.common import to_bytes, from_bytes

import usb
import array
import struct

def bruteforce(device, config, dump_ptr, dump=False):

    addr = config.watchdog_address + 0x50
