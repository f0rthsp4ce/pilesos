import subprocess


class CameraController:
    def __init__(
        self, device: str = "/dev/video0", settings: dict[str, str] = {}
    ) -> None:
        self.device = device
        self.settings = settings
        self.apply_settings()

    def apply_settings(self):
        for setting, value in self.settings.items():
            subprocess.run(
                ["v4l2-ctl", "-d", "/dev/video0", f"--set-ctrl={setting}={value}"]
            )


front_camera = CameraController(
    settings={"auto_exposure": "1", "exposure_time_absolute": "156"}
)
