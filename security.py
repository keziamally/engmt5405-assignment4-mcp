import os
import re
import time
from collections import defaultdict, deque

from dotenv import load_dotenv


load_dotenv()


RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "5"))
RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")
)


# Only allow simple text that makes sense for our dataset filters.
# This blocks SQL-style punctuation such as ', ;, --, etc.
SAFE_TEXT_PATTERN = re.compile(r"^[A-Za-z0-9 _-]+$")


def sanitize_filter_text(
    value: str | None,
    field_name: str,
    max_length: int = 50,
) -> str | None:
    """
    Validate user-supplied filter text.

    Allows letters, numbers, spaces, underscores, and hyphens.
    Rejects suspicious punctuation and overly long input.
    """

    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")

    value = value.strip()

    if not value:
        return None

    if len(value) > max_length:
        raise ValueError(
            f"{field_name} must not exceed {max_length} characters."
        )

    if not SAFE_TEXT_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} contains unsupported characters."
        )

    return value


def validate_limit(limit: int) -> int:
    """
    Validate the maximum number of rows requested.
    """

    if not isinstance(limit, int):
        raise ValueError("limit must be an integer.")

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100.")

    return limit


class RateLimiter:
    """
    Simple in-memory sliding-window rate limiter.

    Each operation name gets its own request history.
    """

    def __init__(
        self,
        max_calls: int = RATE_LIMIT_CALLS,
        window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
    ) -> None:
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        """
        Allow the request if it is below the rate limit.

        Raises ValueError if the limit has been exceeded.
        """

        now = time.monotonic()
        request_times = self.requests[key]

        # Remove requests outside the current time window.
        while (
            request_times
            and now - request_times[0] >= self.window_seconds
        ):
            request_times.popleft()

        if len(request_times) >= self.max_calls:
            raise ValueError(
                "Rate limit exceeded. Please try again later."
            )

        request_times.append(now)

    def reset(self) -> None:
        """
        Clear rate-limit history.

        Useful for testing.
        """
        self.requests.clear()


rate_limiter = RateLimiter()