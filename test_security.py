from security import (
    RateLimiter,
    sanitize_filter_text,
    validate_limit,
)


def test_safe_input() -> None:
    value = sanitize_filter_text("North", "region")
    assert value == "North"
    print("[PASS] Normal filter input accepted")


def test_injection_attempt() -> None:
    malicious_input = "North' OR 1=1 --"

    try:
        sanitize_filter_text(
            malicious_input,
            "region",
        )
    except ValueError:
        print("[PASS] Injection-style input blocked")
        return

    raise AssertionError(
        "Injection-style input was not blocked"
    )


def test_invalid_limit() -> None:
    try:
        validate_limit(500)
    except ValueError:
        print("[PASS] Invalid row limit blocked")
        return

    raise AssertionError(
        "Invalid row limit was not blocked"
    )


def test_rate_limit() -> None:
    limiter = RateLimiter(
        max_calls=3,
        window_seconds=60,
    )

    limiter.check("demo")
    limiter.check("demo")
    limiter.check("demo")

    try:
        limiter.check("demo")
    except ValueError:
        print("[PASS] Rate limit triggered correctly")
        return

    raise AssertionError(
        "Rate limit did not trigger"
    )


if __name__ == "__main__":
    print("Running security tests...\n")

    test_safe_input()
    test_injection_attempt()
    test_invalid_limit()
    test_rate_limit()

    print("\nAll security tests passed.")