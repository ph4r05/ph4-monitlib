import time

from ph4monitlib.flaky import FlakinessDetector


def test_stable_behavior(monkeypatch):
    detector = FlakinessDetector(history_seconds=60, max_flips=2)

    now = 1000
    monkeypatch.setattr(time, "time", lambda: now)
    assert detector.on_state_change("up") == (False, False)

    monkeypatch.setattr(time, "time", lambda: now + 10)
    assert detector.on_state_change("down") == (False, False)

    monkeypatch.setattr(time, "time", lambda: now + 20)
    assert detector.on_state_change("up") == (False, False)


def test_flaky_transition(monkeypatch):
    detector = FlakinessDetector(history_seconds=60, max_flips=2)

    base = 2000
    monkeypatch.setattr(time, "time", lambda: base)
    detector.on_state_change("up")  # no flip yet

    monkeypatch.setattr(time, "time", lambda: base + 5)
    detector.on_state_change("down")  # flip 1

    monkeypatch.setattr(time, "time", lambda: base + 10)
    detector.on_state_change("up")  # flip 2

    monkeypatch.setattr(time, "time", lambda: base + 15)
    is_flaky, changed = detector.on_state_change("down")  # flip 3 → exceeds threshold

    assert is_flaky is True
    assert changed is True


def test_flakiness_recovery(monkeypatch):
    detector = FlakinessDetector(history_seconds=30, max_flips=1)

    base = 3000
    monkeypatch.setattr(time, "time", lambda: base)
    detector.on_state_change("up")

    monkeypatch.setattr(time, "time", lambda: base + 5)
    detector.on_state_change("down")

    # Now it's flaky
    monkeypatch.setattr(time, "time", lambda: base + 10)
    is_flaky, changed = detector.on_state_change("up")
    assert is_flaky is True
    assert changed is True

    # Advance beyond history window so flips expire
    monkeypatch.setattr(time, "time", lambda: base + 45)
    is_flaky, changed = detector.on_state_change("down")
    assert is_flaky is False
    assert changed is True


def test_ignores_repeated_same_state(monkeypatch):
    detector = FlakinessDetector(history_seconds=30, max_flips=2)

    base = 4000
    monkeypatch.setattr(time, "time", lambda: base)
    detector.on_state_change("up")

    monkeypatch.setattr(time, "time", lambda: base + 10)
    is_flaky, changed = detector.on_state_change("up")

    assert is_flaky is False
    assert changed is False
