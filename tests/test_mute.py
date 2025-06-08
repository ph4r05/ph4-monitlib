import datetime

import pytest

from ph4monitlib.mute import DurationParser, Mute, datetime_to_utc_seconds


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("1s", 1),
        ("2m", 120),
        ("3h", 10800),
        ("4d", 345600),
        ("  5m ", 300),
    ],
)
def test_valid_durations(input_str, expected):
    assert DurationParser.str2time(input_str) == expected


@pytest.mark.parametrize(
    "invalid_input",
    [
        "10x",  # invalid unit
        "10",  # no unit
        "",  # empty
        None,  # non-string
        42,  # non-string
    ],
)
def test_invalid_durations(invalid_input):
    with pytest.raises(ValueError):
        DurationParser.str2time(invalid_input)


def test_mute_and_unmute():
    mute = Mute()
    assert not mute.is_muted()

    mute.mute("2s")
    assert mute.is_muted()

    mute.unmute()
    assert not mute.is_muted()


def test_mute_duration_behavior():
    mute = Mute()
    now = datetime.datetime(2023, 1, 1, 12, 0, 0)
    mute._unmute_at = now + datetime.timedelta(seconds=10)

    # Simulate current time before unmute
    assert mute.is_muted(current_time=now + datetime.timedelta(seconds=5)) is True

    # Simulate current time at unmute
    assert mute.is_muted(current_time=now + datetime.timedelta(seconds=10)) is False

    # After unmute
    assert mute.is_muted(current_time=now + datetime.timedelta(seconds=15)) is False


def test_invalid_duration():
    mute = Mute()
    with pytest.raises(ValueError):
        mute.mute("badvalue")


def test_aware_datetime_conversion():
    dt = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    assert datetime_to_utc_seconds(dt) == 1672574400


def test_naive_datetime_assumed_utc():
    dt = datetime.datetime(2023, 1, 1, 12, 0, 0)  # naive datetime
    assert datetime_to_utc_seconds(dt) == 1672574400


def test_non_utc_aware_datetime():
    est = datetime.timezone(datetime.timedelta(hours=-5))
    dt = datetime.datetime(2023, 1, 1, 7, 0, 0, tzinfo=est)  # same as 12:00 UTC
    assert datetime_to_utc_seconds(dt) == 1672574400


def test_roundtrip_now():
    now = datetime.datetime.now(datetime.timezone.utc)
    ts = datetime_to_utc_seconds(now)
    # Allow a 1-second margin for timing drift
    assert abs(now.timestamp() - ts) <= 1
