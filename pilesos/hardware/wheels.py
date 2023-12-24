"""
Main wheels controller. Used for moving the vehicle.

Driver: DRV8801
PDF: https://www.ti.com/lit/ds/symlink/drv8801.pdf
"""

from logging import getLogger

import pigpio

from pilesos.hardware.gpio import gpio

logger = getLogger(__name__)


class WheelController:
    """Class for controlling all wheels of the vehicle."""

    # GPIO pins configuration
    EN: int
    PHASE: int
    # some motors / drivers are connected backwards
    reversed: bool = False

    @staticmethod
    def value_map(value: int, min1: int, max1: int, min2: int, max2: int) -> int:
        """Map one value range to another. Equivalent to Arduino Framework map() function.

        Example:
            # 0..255 -> -10..10
            value_map(98, 0, 255, -10, 10)
        """
        left_span = max1 - min1
        right_span = max2 - min2
        value_scaled = float(value - min1) / float(left_span)
        return round(min2 + (value_scaled * right_span))

    def __init__(self, en: int, phase: int, reversed: bool = False) -> None:
        """Initialize EN, PHASE pins and start PWM"""
        self.EN = en
        self.PHASE = phase
        self.REVERSED = reversed
        # EN pin (driver off)
        gpio.set_mode(self.EN, mode=pigpio.OUTPUT)
        gpio.write(self.EN, pigpio.LOW)
        # PHASE pin (motor off)
        gpio.set_mode(self.PHASE, mode=pigpio.OUTPUT)
        gpio.write(self.PHASE, pigpio.LOW)
        # PHASE PWM 1kHz, 50% duty cycle (stop motor)
        gpio.set_PWM_frequency(user_gpio=self.PHASE, frequency=1000)
        gpio.set_PWM_dutycycle(user_gpio=self.PHASE, dutycycle=50)

    def set_speed(self, speed: int) -> None:
        """Set speed and direction of the wheel.

        Args:
            speed: -100..100

        Examples:
            set_speed(23)
            set_speed(-92)
        """
        logger.debug("speed=%s" % speed)
        if self.REVERSED:
            speed = -speed
        gpio.set_PWM_dutycycle(
            user_gpio=self.PHASE,
            # map -100..100 to 1..255 (minus some edges) where 128 = 50% duty cycle = stop.
            dutycycle=self.value_map(speed, -100, 100, 3, 253),
        )
        if speed == 0:
            # power off if stopped
            gpio.write(self.EN, pigpio.LOW)
        else:
            gpio.write(self.EN, pigpio.HIGH)


left_wheel_controller = WheelController(en=26, phase=16)
right_wheel_controller = WheelController(en=5, phase=13, reversed=True)
