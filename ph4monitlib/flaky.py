import time
import typing
from collections import deque
from typing import Optional


class FlakinessDetector:
    def __init__(self, history_seconds: int, max_flips: int):
        self.history_seconds = history_seconds
        self.max_flips = max_flips
        self.history: typing.Deque[typing.Tuple[float, str]] = deque()
        self.current_state: Optional[str] = None
        self._is_flaky = False

    def on_state_change(self, new_state: str) -> typing.Tuple[bool, bool]:
        now = time.time()
        if new_state == self.current_state:
            return self._is_flaky, False

        self.current_state = new_state
        self.history.append((now, new_state))

        # Remove old events
        while self.history and now - self.history[0][0] > self.history_seconds:
            self.history.popleft()

        flip_count = sum(1 for i in range(1, len(self.history)) if self.history[i][1] != self.history[i - 1][1])

        was_flaky = self._is_flaky
        self._is_flaky = flip_count > self.max_flips
        return self._is_flaky, self._is_flaky != was_flaky
