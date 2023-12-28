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
- [ustreamer](https://github.com/pikvm/ustreamer) — fast webcam streaming
- [pigpiod](https://abyz.me.uk/rpi/pigpio/python.html) — gpio daemon to control several independent PWM generators

### hardware

- disassembled vacuum cleaner robot.
- L298N motor driver.
- 18650 batteries + BMS.
- several voltage converters.

## control chain

state of all controls → json → websocket.

`browser → pilesos.server → pilesos.websocket.input → pilesos.hardware → pigpiod → [gpio] → [motor driver]`

## telemetry chain

telemetry is currently passive. when you trigger a control, cockpit reads current sensor data and sends it back to the client.

`browser ← pilesos.server ← pilesos.websocket.telemetry ← pilesos.hardware ← pigpiod ← [gpio] ← [sensor pins]`

## deploy

```bash
docker compose up -d
```
