"""Async rate-limiter for Groq API calls."""
import asyncio
from pypsa_bot.utils.logging import logger


class RateLimiter:
    """Async queue that enforces a cooldown between Groq API calls.

    Prevents bursting through Groq's rate limit (6,000 tokens/min)
    when multiple Discord users ask questions simultaneously.
    """

    def __init__(self, cooldown_seconds: int = 15):
        self._cooldown = cooldown_seconds
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Acquire the rate limiter. Blocks until cooldown has passed."""
        await self._lock.acquire()

    def release(self):
        """Release after cooldown period."""
        asyncio.get_event_loop().call_later(self._cooldown, self._lock.release)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        self.release()
