BOARD_FAMILY := arduino:avr
# remove :cpu=* for new boards, leave only name 
BOARD := nano:cpu=atmega328old
PORT := /dev/ttyUSB0

deps:
	arduino-cli core update-index
	arduino-cli core install ${BOARD_FAMILY}

	arduino-cli lib update-index
	arduino-cli lib install ArduinoJson
	arduino-cli lib install FastLED

flash:
	arduino-cli compile --verbose --upload --fqbn ${BOARD_FAMILY}:${BOARD} chassis.ino --port ${PORT}
