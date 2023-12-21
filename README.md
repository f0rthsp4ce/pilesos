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
    - [joystick controller](https://github.com/cyrus2281/joystick-controller) — vanilla js joystick
- [ustreamer](https://github.com/pikvm/ustreamer) — fast webcam streaming
- [pigpiod](https://abyz.me.uk/rpi/pigpio/python.html) — gpio daemon to control several independent PWM generators

## control chain

`browser → pilesos.cockpit → pilesos.input → pilesos.hardware → pigpiod → [gpio] → [motor driver]`

## deploy

```bash
docker compose up -d
```
