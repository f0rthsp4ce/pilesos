#include <ArduinoJson.h>
#include <FastLED.h>

// WHEELS
#define WHEEL_L_IN1_PIN 5
#define WHEEL_L_IN2_PIN 9
#define WHEEL_R_IN1_PIN 6
#define WHEEL_R_IN2_PIN 10

// FRONT LED STRIP
#define FRONT_STRIP_DATA_PIN 13
#define FRONT_STRIP_NUM_LEDS 27

// BATTERY & ADC
#define BATTERY_EMPTY_V 22.2
#define BATTERY_FULL_V 25.2    // 6S
#define BATTERY_MAX_V 30       // voltage divider should reduce it to ADC_INPUT_MAX_V
#define ADC_INPUT_MAX_V 4.715  // max ADC value, measure yourself
#define BATTERY_VOLTAGE_PIN A0 // connect to output of voltage divider

/*
hardware control input.
- root fields = optional (you may only update one hardware entity)
- nested fields = mandatory.
{
    "front_strip":[
        int [0..255],
        int [0..255],
        int [0..255]
    ],
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
        "voltage": float,
        "percent": int [0-100]
    }
}
*/
StaticJsonDocument<1024> output;

// front led strip state
CRGB front_strip_leds[FRONT_STRIP_NUM_LEDS];

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

    FastLED.addLeds<NEOPIXEL, FRONT_STRIP_DATA_PIN>(front_strip_leds, FRONT_STRIP_NUM_LEDS);
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

void update_hardware()
{
    // set led strip color
    if (input["front_strip"])
    {
        uint8_t r = input["front_strip"][0];
        uint8_t g = input["front_strip"][1];
        uint8_t b = input["front_strip"][2];
        for (int i = 0; i < FRONT_STRIP_NUM_LEDS; i++)
        {
            front_strip_leds[i] = CRGB(r, g, b);
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
    float adc_v = mapfloat(raw_bat_adc, 0, 1023, 0.0, ADC_INPUT_MAX_V);
    float bat_v = adc_v * (BATTERY_MAX_V / ADC_INPUT_MAX_V);
    int percent = 100 - ((BATTERY_FULL_V - bat_v) / (BATTERY_FULL_V - BATTERY_EMPTY_V) * 100);
    if (percent < 0)
        percent = 0;
    output["battery"]["raw_adc"] = raw_bat_adc;
    output["battery"]["adc_v"] = adc_v;
    output["battery"]["voltage"] = bat_v;
    output["battery"]["percent"] = percent;
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
            serializeJson(output, Serial);
            Serial.println();
            output.remove("error");
            return;
        }
        else
        {
            update_hardware();
        }
    }

    if (millis() % 250 == 0)
    {
        collect_telemetry();
        serializeJson(output, Serial);
        Serial.println();
    }
}
