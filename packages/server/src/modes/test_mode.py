from modes.radio_mode import RadioMode


class TestMode(RadioMode):
    def next(self) -> str:
        return "/etc/liquidsoap/assets/stream-intro.mp3"
