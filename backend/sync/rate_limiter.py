import time
import threading

class RateLimiter:
    """Thread-safe rate limiter using token bucket algorithm (fixed - no recursion)"""
    
    def __init__(self, max_calls: int = 100, period_seconds: int = 60):
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit reached, using iterative approach"""
        while True:
            with self.lock:
                now = time.time()
                
                # Remove old calls outside the window
                self.calls = [t for t in self.calls if now - t < self.period]
                
                if len(self.calls) < self.max_calls:
                    # Can make the call
                    self.calls.append(now)
                    return  # Exit the loop
                
                # Calculate wait time
                oldest_call = min(self.calls)
                wait_time = self.period - (now - oldest_call) + 0.1
            
            # Wait outside the lock
            if wait_time > 0:
                time.sleep(wait_time)
    
    def register_call(self):
        """Register a call for rate limiting"""
        with self.lock:
            self.calls.append(time.time())
