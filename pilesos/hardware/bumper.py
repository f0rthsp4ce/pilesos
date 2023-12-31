"""
Bumper impact sensor. Used to detect front collisions with object.
May optionally run a user-defined callback.
"""

from logging import getLogger
from typing import Callable

import pigpio

from pilesos.hardware.gpio import gpio
from pilesos.hardware.pinout import BumperPinout

logger = getLogger(__name__)


class BumperStateMonitor:
    """Passive bumper collision detector"""

    PIN: int
    ADDITIONAL_CALLBACK: Callable[[bool], None] | None
    collision_detected: bool = False

    def __init__(
        self, pin: int, additional_callback: Callable[[bool], None] | None = None
    ) -> None:
        self.PIN = pin
        self.ADDITIONAL_CALLBACK = additional_callback
        # Initialize GPIO pins
        gpio.set_pull_up_down(gpio=self.PIN, pud=pigpio.PUD_UP)
        gpio.set_mode(self.PIN, pigpio.INPUT)
        gpio.set_glitch_filter(self.PIN, 100_000)  # 100ms

        # Set up trigger
        def callback(pin: int, new_state: int, tick: int):
            # HIGH = no collision
            # LOW = collision
            self.collision_detected = not bool(new_state)
            # run user defined callback
            if self.ADDITIONAL_CALLBACK:
                self.ADDITIONAL_CALLBACK(self.collision_detected)

        gpio.callback(user_gpio=self.PIN, edge=pigpio.EITHER_EDGE, func=callback)


left_bumper = BumperStateMonitor(
    pin=BumperPinout.LEFT, additional_callback=lambda x: logger.debug("left: %s" % x)
)
right_bumper = BumperStateMonitor(
    pin=BumperPinout.RIGHT, additional_callback=lambda x: logger.debug("right: %s" % x)
)
