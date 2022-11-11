import time


class RateLimiter:
    """Rate limiter.

    Provides methods to easily handle APis rate limits
    """

    def __init__(self, req_per_second=1):
        """Init RateLimiter"""
        self.start_time = time.time()
        self.req_per_second = req_per_second

    def reset_timer(self):
        """Reset the rate limiting timer."""
        self.start_time = time.time()

    def wait_for_rate_limit(self):
        """Wait until the API is ready to accept new requests"""
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        time_to_wait = 1 / self.req_per_second
        sleep_time = max((time_to_wait - elapsed_time), 0)
        time.sleep(sleep_time)
