from modes.radio_mode import RadioMode


class TestMode(RadioMode):
    def next() -> str:
        return "/etc/liquidsoap/assets/oops.mp3"
