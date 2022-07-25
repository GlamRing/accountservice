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
            self.backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.dll")
            if self.backend:
                try:
                    self.backend.lib.libusb_set_option.argtypes = [c_void_p, c_int]
                    self.backend.lib.libusb_set_option(self.backend.ctx, 1)  # <--- this is the magic call to enable usbdk mode
                    self.usbdk = True
                except ValueError:
                    log("Failed enabling UsbDk mode, please use 64-Bit Python and 64-Bit UsbDk")
            else:
                self.backend = usb.backend.libusb1.get_backend()
        except usb.core.USBError:
            self.backend = usb.backend.libusb1.get_backend()

        log("Waiting for device")
        if wait:
            self.udev = usb.core.find(idVendor=int(VID, 16), backend=self.backend)
            while self.udev:
                time.sleep(0.25)
                self.udev = usb.core.find(idVendor=int(VID, 16), backend=self.backend)
        self.udev = None
        while not self.udev:
            self.udev = usb.core.find(idVendor=int(VID, 16), backend=self.backend)
            if self.udev:
                break
            time.sleep(0.25)