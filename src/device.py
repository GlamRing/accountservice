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

        log("Found device = {0:04x}:{1:04x}".format(self.udev.idVendor, self.udev.idProduct))
        self.dev = self

        try:
            if self.udev.is_kernel_driver_active(0):
                self.udev.detach_kernel_driver(0)

            if self.udev.is_kernel_driver_active(1):
                self.udev.detach_kernel_driver(1)

        except (NotImplementedError, usb.core.USBError):
            pass

        try:
            self.configuration = self.udev.get_active_configuration()
        except (usb.core.USBError, NotImplementedError) as e:
            if type(e) is usb.core.USBError and e.errno == 13 or type(e) is NotImplementedError:
                log("Failed to enable libusb1, is UsbDk installed?")
                log("Falling back to libusb0 (kamakiri only)")
                self.backend = usb.backend.libusb0.get_backend()
                self.udev = usb.core.find(idVendor=int(VID, 16), backend=self.backend)
                self.libusb0 = True
            try:
                self.udev.set_configuration()
            except AttributeError:
                log("Failed to enable libusb0")
                exit(1)

        if self.udev.idProduct != int(PID, 16):
            self.preloader = True
        else:
            try:
                self.udev.set_configuration(1)
                usb.util.claim_interface(self.udev, 0)
                usb.util.claim_interface(self.udev, 1)
            except usb.core.USBError:
                pass

        cdc_if = usb.util.find_descriptor(self.udev.get_active_configuration(), bInterfaceClass=0xA)
        self.ep_in = usb.util.find_descriptor(cdc_if, custom_match=lambda x: usb.util.endpoint_direction(x.bEndpointAddress) == usb.util.ENDPOINT_IN)
        self.ep_out = usb.util.find_descriptor(cdc_if, custom_match=lambda x: usb.util.endpoint_direction(x.bEndpointAddress) == usb.util.ENDPOINT_OUT)

        try:
            self.udev.ctrl_transfer(0x21, 0x20, 0, 0, array.array('B', to_bytes(BAUD, 4 , '<') + b"\x00\x00\x08"))
        except usb.core.USBError:
            pass

        return self

    @staticmethod
    def check(test, gold):
        if test != gold:
            if type(test) == bytes:
                test = "0x" + test.hex()
            else:
                test = hex(test)

            if type(gold) == bytes:
                gold = "0x" + gold.hex()
            else:
                gold = hex(gold)

            raise RuntimeError("Unexpected output, expected {} got {}".format(gold, test))

    def close(self):
        self.dev = None
        self.rxbuffer = array.array('B')
        try:
            usb.util.release_interface(self.udev, 0)
            usb.util.release_interface(self.udev, 1)
        except Exception:
            pass
        if not self.usbdk:
            try:
                self.udev.reset()
            except Exception:
                pass
        try:
            self.udev.attach_kernel_driver(0)
        except Exception:
            pass
        try:
            self.udev.attach_kernel_driver(1)
        except Exception:
            pass
        if not self.usbdk:
            try:
      