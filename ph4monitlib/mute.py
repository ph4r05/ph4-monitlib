import datetime
import re
from typing import Optional


class DurationParser:
    TIME_MULTIPLIERS = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    @classmethod
    def str2time(cls, time_str: str) -> int:
        """
        Parses a string duration like '10s', '2m', '1h', '3d' into seconds.
        """
        if not isinstance(time_str, str):
            raise ValueError("Input must be a string")

        pattern = r"^(\d+)([smhd])$"
        match = re.match(pattern, time_str.strip())

        if not match:
            raise ValueError(f"Invalid time format: '{time_str}'")

        value, unit = match.groups()
        return int(value) * cls.TIME_MULTIPLIERS[unit]


class Mute:
    def __init__(self):
        self._unmute_at: Optional[datetime.datetime] = None

    def mute(self, duration_str: str):
        """Mute notifications for a duration string like '10s', '5m', etc."""
        seconds = DurationParser.str2time(duration_str)
        self._unmute_at = datetime.datetime.now() + datetime.timedelta(seconds=seconds)

    def mute_until(self, unmute_at: datetime.datetime):
        """Mute until a specific datetime."""
        assert isinstance(unmute_at, datetime.datetime), "unmute_at must be a datetime object"
        self._unmute_at = unmute_at

    def unmute(self):
        """Unmute immediately."""
        self._unmute_at = None

    def is_muted(self, current_time: Optional[datetime.datetime] = None) -> bool:
        """Check if currently muted. Optionally pass in a custom time."""
        now = current_time or datetime.datetime.now()
        return self._unmute_at is not None and now < self._unmute_at


def datetime_to_utc_seconds(dt: datetime.datetime) -> int:
    """Convert a datetime to UTC seconds since epoch."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    else:
        dt = dt.astimezone(datetime.timezone.utc)
    return int(dt.timestamp())


def utc_seconds_to_datetime(seconds: int) -> datetime.datetime:
    """Convert UTC seconds since epoch to a UTC datetime."""
    return datetime.datetime.fromtimestamp(seconds, tz=datetime.timezone.utc)
