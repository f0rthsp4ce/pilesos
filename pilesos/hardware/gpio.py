"""
Public GPIO interface. Usable from any module, simultaneously.
"""
import pigpio

# connect to pigpiod daemon
gpio = pigpio.pi("pigpiod", port=8888)
