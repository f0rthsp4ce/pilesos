# PiLesos

hardware hacked vacuum cleaner.

## components

### raspberry pi 3b+

- [arch linux arm](https://archlinuxarm.org/platforms/armv8/broadcom/raspberry-pi-3) — lightweight and fast distro (optional)
- docker compose — one command build & deploy

### software (dockerized)

most images are alpine based.

- cockpit
    - [fastapi](https://fastapi.tiangolo.com/) — web server for HTML and REST API
    - [fastapi websockets](https://fastapi.tiangolo.com/advanced/websockets/) — realtime input sending
    - [nipplejs](https://www.npmjs.com/package/nipplejs) — vanilla js joystick
    - [rpi-ws281x](https://github.com/rpi-ws281x/rpi-ws281x-python) — library for RGB strip
- [ustreamer](https://github.com/pikvm/ustreamer) — fast webcam streaming
- [pigpiod](https://abyz.me.uk/rpi/pigpio/python.html) — gpio daemon to control several independent PWM generators

### hardware

- disassembled vacuum cleaner robot.
- L298N motor driver.
- 18650 batteries + BMS.
- several voltage converters.
- WS2818B led strip.

## control chain

state of all controls → json → websocket.

`browser → pilesos.server → pilesos.websocket.input → pilesos.hardware → pigpiod → [gpio] → [motor driver]`

## telemetry chain

telemetry is sent every 100ms.

`browser ← pilesos.server ← pilesos.websocket.telemetry ← pilesos.hardware ← pigpiod ← [gpio] ← [sensor pins]`

## deploy

```bash
git clone https://github.com/f0rthsp4ce/pilesos
cd pilesos
docker compose up -d
```
