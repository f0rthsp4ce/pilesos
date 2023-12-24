"""
Bumper impact sensor. Used to detect front collisions with object.
May optionally run a user-defined callback.
"""

from audioop import add
from logging import getLogger
from typing import Callable

import pigpio

from pilesos.hardware.gpio import gpio

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

        # Set up trigger
        def callback(pin: int, new_state: int, tick: int):
            # HIGH = collision
            # LOW = no collision
            self.collision_detected = bool(new_state)
            # run user defined callback
            if self.ADDITIONAL_CALLBACK:
                self.ADDITIONAL_CALLBACK(self.collision_detected)

        gpio.callback(user_gpio=self.PIN, edge=pigpio.EITHER_EDGE, func=callback)


left_bumper = BumperStateMonitor(
    pin=17, additional_callback=lambda x: logger.info("left: %s" % x)
)
right_bumper = BumperStateMonitor(
    pin=27, additional_callback=lambda x: logger.info("right: %s" % x)
)
