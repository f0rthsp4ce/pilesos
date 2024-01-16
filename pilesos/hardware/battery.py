import logging
from dataclasses import dataclass

from pilesos.hardware.analog import PCF8591T, AnalogReader, pcf
from pilesos.hardware.utils import value_map

logger = logging.getLogger(__name__)


# 18650 6S
V_MIN = 22.2
V_MAX = 25.2


@dataclass
class BatteryState:
    volts: float
    percent: int


battery_raw_adc = AnalogReader(ain=PCF8591T.AIN.A0, pcf=pcf)


def get_battery() -> BatteryState:
    raw = battery_raw_adc.read()
    logger.info(f"raw: {raw}")
    adc_volts = value_map(raw, 0, 255, 0, 5)
    battery_volts = adc_volts * 10
    return BatteryState(volts=battery_volts, percent=0)
