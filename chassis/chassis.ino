#include <ArduinoJson.h>
#include <FastLED.h>

// PINOUT
#define WHEEL_L_IN1_PIN 4
#define WHEEL_L_IN2_PIN 5
#define WHEEL_R_IN1_PIN 6
#define WHEEL_R_IN2_PIN 7

#define FRONT_STRIP_DATA_PIN 13
#define BATTERY_VOLTAGE_PIN A0

// SETTINGS
#define FRONT_STRIP_NUM_LEDS 27

// json object with parsed serial input
StaticJsonDocument<1204> input;
// front led strip state
CRGB front_strip_leds[FRONT_STRIP_NUM_LEDS];

void setup()
{
    Serial.begin(115200);
    Serial.setTimeout(10); // don't wait if sender hangs
    FastLED.addLeds<NEOPIXEL, FRONT_STRIP_DATA_PIN>(front_strip_leds, FRONT_STRIP_NUM_LEDS);
}

void loop()
{
    if (Serial.available() > 0)
    {
        // receive and parse json
        String inputJsonString = Serial.readStringUntil('\n');
        DeserializationError error = deserializeJson(input, inputJsonString);
        if (error)
        {
            Serial.print('{"error":"');
            Serial.print(error.c_str());
            Serial.println('"}');
            return;
        }

        // update led strip color
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
    }
}
