from src.common import to_bytes, from_bytes

import usb
import array
import struct

def bruteforce(device, config, dump_ptr, dump=False):

    addr = config.watchdog_address + 0x50

    # We don't need to wait long, if we succeeded
    # noinspection PyBroadException
    try:
        device.dev.timeout = 1
    except Exception:
        pass

    udev = device.udev

    try:
        # noinspection PyProtectedMember
        udev._ctx.managed_claim_interface = lambda *args, **kwargs: None
    except AttributeError as e:
        raise RuntimeError("libusb is not installed for port {}".format(device.dev.port)) from e

    linecode = udev.ctrl_transfer(0xA1, 0x21, 0, 0,