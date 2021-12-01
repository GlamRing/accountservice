# Bypass utility
Small utility to disable bootrom protection(sla and daa)

## Payloads
https://github.com/MTK-bypass/exploits_collection

## Usage on Windows
Skip steps 1-3 after first usage

1. Install [python (64-bit)](https://www.python.org/downloads)(select "Add Python X.X to PATH")
2. Install [UsbDk (64-bit)](https://github.com/daynix/UsbDk/releases)
3. Install pyusb, json5 with command:
```
pip install pyusb json5
```
4. Run this command and connect your powered off phone with volume+ button, you should get "Protection disabled" at the end
```
python main.py
```
5. After that, without disconnecting phone, run SP Flash Tool


## Usage on Linux
Skip steps 1-2 after first usage
To use k