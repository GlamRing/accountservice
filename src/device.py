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
    def __init__(self, port=None):
        self.udev = None
        self.dev = None
        self.rxbuffer = array.array('B')
        self.preloader = False
        self.timeout = TIMEOUT
        self.usbdk = False
        self.libusb0 = False

        if os.name == 'nt':
            try:
                file_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
                try:
                    os.add_dll_directory(file_dir)
                except Exception:
                    pass
                os.environ['PATH'] = file_dir + ';' + os.environ['PATH']
            except Exception:
                pass

    def find(self, wait=False):
        if self.dev:
            raise RuntimeError("Device already found")

        try:
         