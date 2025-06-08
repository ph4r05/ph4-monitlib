import time
import typing
from collections import deque
from typing import Optional


class SlidingWindowRateLimiter:
    def __init__(self, max_events: int, per_seconds: int):
        """
        :param max_events: Maximum allowed events in the time window.
        :param per_seconds: Size of the sliding window in seconds.
        """
        self.max_events = max_events
        self.per_seconds = per_seconds
        self.events: typing.Deque[float] = deque()

    def on_event(self) -> typing.Tuple[bool, Optional[int]]:
        """
        Record an event and check if it's allowed.
        :return: (allowed: bool, retry_after: Optional[int])
        """
        now = time.time()

        # Remove expired events
        while self.events and now - self.events[0] >= self.per_seconds:
            self.events.popleft()

        if len(self.events) < self.max_events:
            self.events.append(now)
            return True, None

        # Rate limited
        retry_after = int(self.per_seconds - (now - self.events[0]))
        return False, retry_after
