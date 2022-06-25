from src.common import to_bytes, from_bytes
from src.logger import log
import usb
import usb.backend.libusb1
import usb.backend.libusb0
from ctypes import c_void_p, c_int
import array
import os

import time

BAUD = 115200
TIMEOUT = 1
VID = "0E8D"
PID = "0003"


class Device:
    def