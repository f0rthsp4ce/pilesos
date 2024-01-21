import logging
import subprocess

logger = logging.getLogger(__name__)


class CameraController:
    def __init__(
        self, device: str = "/dev/video0", settings: dict[str, str] = {}
    ) -> None:
        self.device = device
        self.settings = settings
        self.apply_settings()

    def apply_settings(self):
        for setting, value in self.settings.items():
            p = subprocess.run(
                ["v4l2-ctl", "-d", "/dev/video0", f"--set-ctrl={setting}={value}"],
                capture_output=True,
            )
            if p.stderr or p.stdout:
                logger.error(f"{p.stdout=}, {p.stderr=}")


front_camera = CameraController(
    settings={"auto_exposure": "1", "exposure_time_absolute": "156"}
)
