"""
Rate limiter for Google Gemini API calls.
Enforces free tier limits: 15 requests per minute.
"""
import time
import asyncio
from typing import List


class GeminiRateLimiter:
    """
    Rate limiter for Gemini API to enforce free tier limits.

    Free tier limits:
    - 15 requests per minute
    - 1,500 requests per day
    """

    def __init__(self, max_requests_per_minute: int = 15, max_requests_per_day: int = 1500):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_minute: Maximum requests allowed per minute
            max_requests_per_day: Maximum requests allowed per day
        """
        self.max_per_minute = max_requests_per_minute
        self.max_per_day = max_requests_per_day
        self.minute_window = 60  # seconds
        self.day_window = 86400  # seconds (24 hours)

        # Track request timestamps
        self.minute_requests: List[float] = []
        self.day_requests: List[float] = []

    async def acquire(self) -> None:
        """
        Acquire permission to make an API request.
        Blocks until a slot is available if at capacity.
        """
        now = time.time()

        # Clean up old requests outside windows
        self._cleanup_old_requests(now)

        # Check minute limit
        while len(self.minute_requests) >= self.max_per_minute:
            # Calculate wait time until oldest request expires
            oldest_request = self.minute_requests[0]
            wait_time = self.minute_window - (now - oldest_request)

            if wait_time > 0:
                await asyncio.sleep(wait_time + 0.1)  # Add small buffer
                now = time.time()
                self._cleanup_old_requests(now)
            else:
                self._cleanup_old_requests(now)
                break

        # Check day limit
        if len(self.day_requests) >= self.max_per_day:
            # Calculate wait time until oldest daily request expires
            oldest_request = self.day_requests[0]
            wait_time = self.day_window - (now - oldest_request)

            if wait_time > 0:
                raise Exception(
                    f"Daily API quota exceeded. Try again in {int(wait_time / 60)} minutes."
                )

        # Record this request
        self.minute_requests.append(now)
        self.day_requests.append(now)

    def _cleanup_old_requests(self, current_time: float) -> None:
        """Remove requests outside the tracking windows."""
        # Remove minute requests older than 60 seconds
        self.minute_requests = [
            t for t in self.minute_requests
            if current_time - t < self.minute_window
        ]

        # Remove day requests older than 24 hours
        self.day_requests = [
            t for t in self.day_requests
            if current_time - t < self.day_window
        ]

    def get_requests_remaining(self) -> dict:
        """Get remaining requests for current windows."""
        now = time.time()
        self._cleanup_old_requests(now)

        return {
            "minute": {
                "used": len(self.minute_requests),
                "remaining": self.max_per_minute - len(self.minute_requests),
                "limit": self.max_per_minute
            },
            "day": {
                "used": len(self.day_requests),
                "remaining": self.max_per_day - len(self.day_requests),
                "limit": self.max_per_day
            }
        }

    def reset(self) -> None:
        """Reset all request tracking (for testing)."""
        self.minute_requests = []
        self.day_requests = []
