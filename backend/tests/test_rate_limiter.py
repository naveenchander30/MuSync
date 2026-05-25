import pytest
import time
import threading
from backend.sync.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test rate limiter functionality"""
    
    def test_allows_calls_within_limit(self):
        limiter = RateLimiter(max_calls=10, period_seconds=60)
        
        for i in range(10):
            limiter.wait_if_needed()
        
        assert len(limiter.calls) == 10
    
    def test_blocks_when_limit_reached(self):
        limiter = RateLimiter(max_calls=5, period_seconds=1)
        
        for i in range(5):
            limiter.wait_if_needed()
        
        # Next call should wait
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        
        # Should have waited approximately 1 second
        assert elapsed >= 0.9
    
    def test_resets_after_period(self):
        limiter = RateLimiter(max_calls=5, period_seconds=1)
        
        for i in range(5):
            limiter.wait_if_needed()
        
        # Wait for period to expire
        time.sleep(1.1)
        
        # Should allow new calls immediately
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        
        assert elapsed < 0.1
    
    def test_register_call(self):
        limiter = RateLimiter(max_calls=10, period_seconds=60)
        
        assert len(limiter.calls) == 0
        limiter.register_call()
        assert len(limiter.calls) == 1
    
    def test_thread_safety(self):
        limiter = RateLimiter(max_calls=100, period_seconds=60)
        threads = []
        
        def make_call():
            for _ in range(10):
                limiter.wait_if_needed()
        
        # Create 10 threads, each making 10 calls
        for _ in range(10):
            t = threading.Thread(target=make_call)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have exactly 100 calls registered
        assert len(limiter.calls) == 100
    
    def test_old_calls_are_cleaned(self):
        limiter = RateLimiter(max_calls=5, period_seconds=1)
        
        # Make 5 calls
        for i in range(5):
            limiter.register_call()
        
        # Wait for period to expire
        time.sleep(1.1)
        
        # Make another call - should clean old calls
        limiter.wait_if_needed()
        
        # Only the new call should remain
        assert len(limiter.calls) == 1


class TestRateLimiterNoRecursion:
    """Test that rate limiter doesn't use recursion"""
    
    def test_no_stack_overflow(self):
        """Test that rate limiter handles long waits without stack overflow"""
        limiter = RateLimiter(max_calls=1, period_seconds=1)
        
        # Make one call
        limiter.wait_if_needed()
        
        # Next call should wait without recursion issues
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        
        # Should wait approximately 1 second
        assert elapsed >= 0.9
