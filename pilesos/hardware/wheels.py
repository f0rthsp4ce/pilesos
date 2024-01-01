"""
Main wheels controller. Used for moving the vehicle.

Driver: L298N
"""

from logging import getLogger

import pigpio

from pilesos.hardware.gpio import gpio
from pilesos.hardware.pinout import WheelsPinout

logger = getLogger(__name__)


class WheelController:
    # GPIO pins configuration
    EN: int
    IN1: int
    IN2: int
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

    def __init__(self, EN: int, IN1: int, IN2: int, reversed: bool = False) -> None:
        """Initialize EN, IN1, IN2 pins and start PWM"""
        self.EN = EN
        self.IN1 = IN1
        self.IN2 = IN2
        self.reversed = reversed
        # Set all pins as output, LOW
        for pin in self.EN, self.IN1, self.IN2:
            gpio.set_mode(self.EN, mode=pigpio.OUTPUT)
            gpio.write(self.EN, pigpio.LOW)
        # EN PWM 1kHz, 0% duty cycle (stop motor)
        gpio.set_PWM_frequency(user_gpio=self.EN, frequency=1000)
        gpio.set_PWM_dutycycle(user_gpio=self.EN, dutycycle=0)

    def set_speed(self, speed: int) -> None:
        """Set speed and direction of the wheel.

        Args:
            speed: -100..100

        Examples:
            set_speed(23)
            set_speed(-92)
        """
        logger.debug("speed=%s" % speed)
        if self.reversed:
            speed = -speed
        # set motor direction
        if speed < 0:
            gpio.write(self.IN1, pigpio.HIGH)
            gpio.write(self.IN2, pigpio.LOW)
        if speed > 0:
            gpio.write(self.IN1, pigpio.LOW)
            gpio.write(self.IN2, pigpio.HIGH)
        if speed == 0:
            gpio.write(self.IN1, pigpio.LOW)
            gpio.write(self.IN2, pigpio.LOW)
        # set motor speed
        gpio.set_PWM_dutycycle(
            user_gpio=self.EN,
            # map 0..100 to 1..255
            dutycycle=self.value_map(abs(speed), 0, 100, 0, 255),
        )


left_wheel_controller = WheelController(
    EN=WheelsPinout.ENA,
    IN1=WheelsPinout.IN1,
    IN2=WheelsPinout.IN2,
    reversed=True,
)
right_wheel_controller = WheelController(
    EN=WheelsPinout.ENB,
    IN1=WheelsPinout.IN3,
    IN2=WheelsPinout.IN4,
)
