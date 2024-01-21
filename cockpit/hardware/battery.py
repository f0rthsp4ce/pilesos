import logging
from dataclasses import dataclass

from pilesos.hardware.analog import a3
from pilesos.hardware.utils import value_map

logger = logging.getLogger(__name__)


# 18650 6S
V_MIN = 22.2
V_MAX = 25.2


@dataclass
class BatteryState:
    volts: float
    percent: int


def get_battery() -> BatteryState:
    raw = a3.read()
    logger.info(f"raw: {raw}")
    # there is ~4.16V-4.19V on the module, idk why not 5V
    adc_volts = value_map(raw, 0, 255, 0, 4.19)
    battery_volts = adc_volts * 10
    return BatteryState(volts=round(battery_volts, 1), percent=0)
