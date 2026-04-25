from modes.radio_mode import RadioMode
from modes.test_mode import TestMode


class State:
    mode: RadioMode = TestMode()
