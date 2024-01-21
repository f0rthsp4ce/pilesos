from enum import Enum

import smbus2


class PCF8591T:
    class AIN(int, Enum):
        A0 = 0x40
        A1 = 0x41
        A2 = 0x42
        A3 = 0x43

    def __init__(self, i2c_bus: int = 0, pcf_addr: int = 0x48) -> None:
        self.pcf_addr = pcf_addr
        self.bus = smbus2.SMBus(i2c_bus)

    def read_adc(self, ain: AIN) -> float:
        self.bus.write_byte(self.pcf_addr, ain)
        # you need to read byte twice and discard the fist reading
        _ = self.bus.read_byte(self.pcf_addr)
        # useful data
        value = self.bus.read_byte(self.pcf_addr)
        return value


class AnalogReader:
    def __init__(self, ain: PCF8591T.AIN, pcf: PCF8591T) -> None:
        self.pcf = pcf
        self.ain = ain

    def read(self):
        return self.pcf.read_adc(self.ain)


pcf = PCF8591T(i2c_bus=1)

a0 = AnalogReader(ain=PCF8591T.AIN.A0, pcf=pcf)
a1 = AnalogReader(ain=PCF8591T.AIN.A1, pcf=pcf)
a2 = AnalogReader(ain=PCF8591T.AIN.A2, pcf=pcf)
a3 = AnalogReader(ain=PCF8591T.AIN.A3, pcf=pcf)
