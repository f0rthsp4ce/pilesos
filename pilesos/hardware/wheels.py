"""
Main wheels controller. Used for moving the vehicle.

Driver: DRV8801
PDF: https://www.ti.com/lit/ds/symlink/drv8801.pdf
"""

from logging import getLogger
from typing import Literal, Union

import pigpio

from pilesos.hardware.gpio import gpio

logger = getLogger(__name__)


# pin configuration
class LeftWheel:
    EN = 5
    PHASE = 12


# pin configuration
class RightWheel:
    EN = 6
    PHASE = 13


def value_map(value: int, l_min: int, l_max: int, r_min: int, r_max: int) -> int:
    """
    Map one value range to another.

    Example:
        # 0..255 -> -10..10
        value_map(98, 0, 255, -10, 10)
    """
    left_span = l_max - l_min
    right_span = r_max - r_min
    value_scaled = float(value - l_min) / float(left_span)
    return round(r_min + (value_scaled * right_span))


class WheelsController:
    """
    Class for controlling all wheels of the vehicle.
    """

    def __init__(self) -> None:
        """
        Initialize all pins.
        """
        for pin in (
            LeftWheel.EN,
            LeftWheel.PHASE,
            RightWheel.EN,
            RightWheel.PHASE,
        ):
            gpio.set_mode(pin, mode=pigpio.OUTPUT)
            gpio.write(pin, pigpio.LOW)
        gpio.set_PWM_frequency(user_gpio=LeftWheel.PHASE, frequency=1000)
        gpio.set_PWM_frequency(user_gpio=RightWheel.PHASE, frequency=1000)

    def set_speed(self, wheel: Union[Literal["L"], Literal["R"]], speed: int) -> None:
        """
        Set speed and direction of the wheel.

        Args:
            wheel: 'L' or 'R'
            speed: -100..100

        Examples:
            set_speed("L", 23)
            set_speed("R", -92)
        """
        logger.debug("wheel=%s speed=%s" % (wheel, speed))
        w = LeftWheel if wheel == "L" else RightWheel

        gpio.set_PWM_dutycycle(
            user_gpio=w.PHASE,
            # map -100..100 to 1..255 where 128 = 50% duty cycle = stop.
            dutycycle=value_map(speed, -100, 100, 3, 254),
        )

        if speed == 0:
            # power off if stopped
            gpio.write(w.EN, pigpio.LOW)
        else:
            gpio.write(w.EN, pigpio.HIGH)


wheels_controller = WheelsController()
