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
        config = open("default_config.json5")
        self.from_file(config, hw_code)
        config.close()

        return self

    def from_file(self, config, hw_code):
        hw_code = hex(hw_code)

        config = json5.load(config)

        if hw_code in config:
  