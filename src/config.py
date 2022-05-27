import json5


class Config:
    watchdog_address: int = 0x10007000
    uart_base: int = 0x11002000
    payload_address: int = 0x100A00
    var_0: int = None
    var_1: int = 0xA
    payload: str
    crash_method: int = 0
    ptr_usbdl: int = None
    ptr_da: int = None

    def default(self, hw_code):
        config = open("default_c