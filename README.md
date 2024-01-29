# PiLesos

~~hardware hacked~~ rebuilt vacuum cleaner.

## components

**cockpit (raspberry pi)** — web robot control, sends command to chassis over uart, streams rpi camera over http.
- [fastapi](https://fastapi.tiangolo.com/) — web server for HTML and REST API
- [fastapi websockets](https://fastapi.tiangolo.com/advanced/websockets/) — realtime input sending
- [nipplejs](https://www.npmjs.com/package/nipplejs) — vanilla js joystick
- [ustreamer](https://github.com/pikvm/ustreamer) — fast webcam streaming

**chassis (arduino nano)** — receives json over uart and controls all the hardware
- [ArduinoJson](https://arduinojson.org/) — fast input/output parsing
- [FastLED](https://fastled.io/) — led strip control

## build & deploy

- arduino chassis firmware build:

    install `arduino-cli`, connect arduino nano.

    ```bash
    cd chassis
    make all
    ```

- raspberry pi cockpit deploy:

    ```bash
    apt install docker.io docker-compose
    cd cockpit
    export DOCKER_BUILDKIT=1
    docker compose up -d
    ```

## required hardware

- raspberry pi 3 / 4
- arduino nano / leonardo (any board w/ 10-bit adc for precise battery reading)
