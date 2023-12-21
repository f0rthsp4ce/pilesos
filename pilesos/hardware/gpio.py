"""
Public GPIO interface. Usable from any module, simultaneously.
"""
import pigpio
from logging import getLogger

logger = getLogger(__name__)

gpio: pigpio.pi

# connect to pigpiod daemon
gpio = pigpio.pi("pigpiod", port=8888, show_errors=False)
if not gpio.connected:
    # virtual environment without gpio
    from unittest.mock import MagicMock

    gpio.set_mode = MagicMock()
    gpio.write = MagicMock()
    gpio.set_PWM_frequency = MagicMock()
    gpio.set_PWM_dutycycle = MagicMock()

    logger.warning("USING MOCKED GPIO. NO REAL PINS FOUND.")
