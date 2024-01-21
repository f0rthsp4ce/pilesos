BOARD_FAMILY := arduino:avr
# remove :cpu=* for new boards, leave only name 
BOARD := nano:cpu=atmega328old
PORT := /dev/ttyUSB0

flash:
# install compiler for board family
	arduino-cli core update-index
	arduino-cli core install ${BOARD_FAMILY}
# install libraries & dependences
	arduino-cli lib update-index
	arduino-cli lib install ArduinoJson
	arduino-cli lib install FastLED
# compile and flash the firmware
	arduino-cli compile --verbose --upload --fqbn ${BOARD_FAMILY}:${BOARD} chassis.ino --port ${PORT}
