from __future__ import annotations

import asyncio
import logging
from typing import Any

from rpi_ws281x import RGBW, PixelStrip

from pilesos.hardware.pinout import StripPinout

logger = logging.getLogger(__name__)


def wheel(pos: int):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return RGBW(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return RGBW(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return RGBW(0, pos * 3, 255 - pos * 3)


class StripEffect:
    def __call__(self, strip: PixelStrip, *args: Any, **kwds: Any) -> Any:
        return NotImplemented


class ColorWipeEffect(StripEffect):
    """Wipe color across display a pixel at a time."""

    def __init__(self, color: RGBW, wait_ms: int = 50) -> None:
        self.color = color
        self.wait_ms = wait_ms

    async def __call__(self, strip: PixelStrip) -> Any:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.color)
            strip.show()
            await asyncio.sleep(self.wait_ms / 1000.0)


class RainbowCycleEffect(StripEffect):
    """Wipe color across display a pixel at a time."""

    def __init__(self, iterations: int, wait_ms: int = 50) -> None:
        self.iterations = iterations
        self.wait_ms = wait_ms

    async def __call__(
        self,
        strip: PixelStrip,
    ) -> Any:
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * self.iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(
                    i, wheel(((i * 256 // strip.numPixels()) + j) & 255)
                )
            strip.show()
            await asyncio.sleep(self.wait_ms / 1000.0)


class StripController:
    def __init__(self, pin: int, led_count: int) -> None:
        self.pin: int = pin
        self.led_count: int = led_count
        self.current_effect: asyncio.Task | None = None
        self.strip = PixelStrip(
            pin=self.pin,
            num=self.led_count,
        )
        self.mocked = False
        try:
            self.strip.begin()
        except RuntimeError as e:
            if (
                str(e)
                == "ws2811_init failed with code -3 (Hardware revision is not supported)"
            ):
                logger.warning("WS2811 INIT FAILED. USING FAKE LED STRIP.")
                self.mocked = True

    async def set_effect(self, effect: StripEffect):
        if self.mocked:
            return
        if self.current_effect and not self.current_effect.done():
            self.current_effect.cancel()
        self.current_effect = asyncio.create_task(effect(strip=self.strip))


bumper_strip = StripController(pin=StripPinout.DIN, led_count=27)
