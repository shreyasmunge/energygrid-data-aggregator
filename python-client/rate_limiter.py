import time

class RateLimiter:
    def __init__(self, min_interval_seconds=1.0):
        self.min_interval = min_interval_seconds
        self.last_request_time = 0.0

    def wait(self):
        now = time.monotonic()
        elapsed = now - self.last_request_time

        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        self.last_request_time = time.monotonic()
