#define ARDUINOJSON_USE_LONG_LONG 1
#include <ArduinoJson.h>
#include <FastLED.h>

// WHEELS
#define WHEEL_L_IN1_PIN 6
#define WHEEL_L_IN2_PIN 10
#define WHEEL_L_FEEDBACK_PIN 2
#define WHEEL_R_IN1_PIN 5
#define WHEEL_R_IN2_PIN 9
#define WHEEL_R_FEEDBACK_PIN 3
#define WHEEL_MAX_FEEDBACK

// FRONT LED STRIP
#define FRONT_STRIP_DATA_PIN 13
#define FRONT_STRIP_NUM_LEDS 27

// BUMPER
#define BUMPER_L_PIN 7
#define BUMPER_R_PIN 8

// BATTERY & ADC
#define BATTERY_VOLTAGE_PIN A0 // connect to output of voltage divider
#define BATTERY_EMPTY_V 22
#define BATTERY_FULL_V 25 // 6S
#define BATTERY_MAX_V 30  // voltage divider should reduce it to max ADC value (1023)

/*
hardware control input.
- root fields = optional (you may only update one hardware entity)
- nested fields = mandatory.
{
    "front_strip": "FF00FF",
    "wheels": {
        "left": int [-255..255],
        "right": int [-255..255]
    }
}
*/
StaticJsonDocument<1024> input;

/*
telemetry to be sent back (optionally with error message).
{
    "error": string,
    "battery": {
        "raw_adc": int [0..1023],
        "adc_v": float,
        "volts": float,
        "percent": int [0-100]
    },
    "bumper": {
        "left": bool,
        "right", bool
    },
    "wheels_speed": {
        "left": int
        "right": int
    }
}
*/
StaticJsonDocument<1024> output;

// front led strip state
CRGB front_strip_leds[FRONT_STRIP_NUM_LEDS];
// wheels feedback
uint64_t left_wheel_counter = 0;
uint64_t right_wheel_counter = 0;
void left_wheel_feedback_interrupt()
{
    left_wheel_counter += 1;
}
void right_wheel_feedback_interrupt()
{
    right_wheel_counter += 1;
}

// utility
float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
{
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void setup()
{
    Serial.begin(115200);
    Serial.setTimeout(10); // don't wait if sender hangs

    pinMode(BATTERY_VOLTAGE_PIN, INPUT);
    pinMode(FRONT_STRIP_DATA_PIN, OUTPUT);
    pinMode(WHEEL_L_IN1_PIN, OUTPUT);
    pinMode(WHEEL_L_IN2_PIN, OUTPUT);
    pinMode(WHEEL_R_IN1_PIN, OUTPUT);
    pinMode(WHEEL_R_IN2_PIN, OUTPUT);
    attachInterrupt(digitalPinToInterrupt(WHEEL_L_FEEDBACK_PIN), left_wheel_feedback_interrupt, RISING);
    attachInterrupt(digitalPinToInterrupt(WHEEL_R_FEEDBACK_PIN), right_wheel_feedback_interrupt, RISING);

    FastLED.addLeds<NEOPIXEL, FRONT_STRIP_DATA_PIN>(front_strip_leds, FRONT_STRIP_NUM_LEDS);
}

void update_hardware()
{
    // set led strip color
    if (input["front_strip"])
    {
        for (int i = 0; i < FRONT_STRIP_NUM_LEDS; i++)
        {
            front_strip_leds[i] = strtol(input["front_strip"], NULL, 0);
            FastLED.show();
        }
    }

    // set motor direction and speed
    if (input["wheels"])
    {
        set_motor_speed(WHEEL_L_IN1_PIN, WHEEL_L_IN2_PIN, input["wheels"]["left"]);
        set_motor_speed(WHEEL_R_IN1_PIN, WHEEL_R_IN2_PIN, input["wheels"]["right"]);
    }
}

void collect_telemetry()
{
    // read battery voltage
    int raw_bat_adc = analogRead(BATTERY_VOLTAGE_PIN);
    float bat_v = mapfloat(raw_bat_adc, 0, 1023, 0.0, BATTERY_MAX_V);
    float volts = ((int)(bat_v * 10)) / 10.0; // leave only 1 decimal place
    int percent = 100 - ((BATTERY_FULL_V - volts) / (BATTERY_FULL_V - BATTERY_EMPTY_V) * 100);
    if (percent < 0)
        percent = 0;
    output["battery"]["raw_adc"] = raw_bat_adc;
    output["battery"]["volts"] = volts;
    output["battery"]["percent"] = percent;

    // read bumpers
    output["bumper"]["left"] = !digitalRead(BUMPER_L_PIN);
    output["bumper"]["right"] = !digitalRead(BUMPER_R_PIN);

    // read wheel rpm
    output["wheels_speed"]["left"] = left_wheel_counter;
    output["wheels_speed"]["right"] = right_wheel_counter;
}

void set_motor_speed(int IN1, int IN2, int speed)
{
    if (speed < 0)
    {
        analogWrite(IN1, 0);
        analogWrite(IN2, abs(speed));
    }
    if (speed > 0)
    {
        analogWrite(IN1, abs(speed));
        analogWrite(IN2, 0);
    }
    if (speed == 0)
    {
        analogWrite(IN1, 0);
        analogWrite(IN2, 0);
    }
}

void loop()
{
    // receive commands
    if (Serial.available() > 0)
    {
        // receive and parse json
        String inputJsonString = Serial.readStringUntil('\n');
        DeserializationError json_err = deserializeJson(input, inputJsonString);
        if (json_err)
        {
            output["error"] = json_err.c_str();
            return;
        }
        else
        {
            update_hardware();
        }
    }

    if (millis() % 50 == 0)
    {
        collect_telemetry();
        serializeJson(output, Serial);
        Serial.println();
        output.remove("error");
        left_wheel_counter = 0;
        right_wheel_counter = 0;
    }
}
