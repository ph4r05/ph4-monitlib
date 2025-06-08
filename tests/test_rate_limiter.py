import time

from ph4monitlib.rate_limit import SlidingWindowRateLimiter


def test_allows_events_within_limit():
    limiter = SlidingWindowRateLimiter(max_events=3, per_seconds=60)

    assert limiter.on_event()[0] is True
    assert limiter.on_event()[0] is True
    assert limiter.on_event()[0] is True


def test_rate_limits_after_max_events():
    limiter = SlidingWindowRateLimiter(max_events=2, per_seconds=60)

    assert limiter.on_event()[0] is True
    assert limiter.on_event()[0] is True
    allowed, retry = limiter.on_event()
    assert allowed is False
    assert retry > 0


def test_allows_event_after_window_expires(monkeypatch):
    limiter = SlidingWindowRateLimiter(max_events=2, per_seconds=10)

    now = time.time()
    monkeypatch.setattr(time, "time", lambda: now)
    assert limiter.on_event()[0] is True
    assert limiter.on_event()[0] is True

    # Should be rate limited
    allowed, _ = limiter.on_event()
    assert allowed is False

    # Advance time by 11 seconds, first event should expire
    monkeypatch.setattr(time, "time", lambda: now + 11)
    assert limiter.on_event()[0] is True


def test_retry_time_decreases(monkeypatch):
    times = [1000, 1005, 1010]  # Simulated timestamps

    limiter = SlidingWindowRateLimiter(max_events=1, per_seconds=10)

    # Override time.time() to cycle through these timestamps
    time_iter = iter(times)
    monkeypatch.setattr(time, "time", lambda: next(time_iter))

    # At time 1000: allow first event
    assert limiter.on_event()[0] is True

    # At time 1005: should be rate limited with 5 seconds remaining
    allowed, retry = limiter.on_event()
    assert allowed is False
    assert retry == 5

    # At time 1010: the 10s window has passed, so event is allowed again
    assert limiter.on_event()[0] is True
