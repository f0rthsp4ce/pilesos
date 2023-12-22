"""
Public GPIO interface. Usable from any module, simultaneously.
"""
from logging import getLogger

import pigpio

logger = getLogger(__name__)

gpio: pigpio.pi

# connect to pigpiod daemon
gpio = pigpio.pi(host="pigpiod", port=8888)
if not gpio.connected:
    # if pigpiod daemon is unavailable, create a virtual mock interface
    logger.warning("USING MOCKED GPIO. NO REAL PINS ARE USED.")
    from unittest.mock import MagicMock

    gpio.set_mode = MagicMock()
    gpio.write = MagicMock()
    gpio.set_PWM_frequency = MagicMock()
    gpio.set_PWM_dutycycle = MagicMock()
