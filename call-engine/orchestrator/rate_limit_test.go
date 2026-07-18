package orchestrator

import (
	"sync"
	"testing"
	"time"
)

type rateLimiter struct {
	mu       sync.Mutex
	lastCall time.Time
	minGap   time.Duration
}

func newRateLimiter(minGap time.Duration) *rateLimiter {
	return &rateLimiter{minGap: minGap}
}

func (r *rateLimiter) Allow() bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	now := time.Now()
	if now.Sub(r.lastCall) < r.minGap {
		return false
	}
	r.lastCall = now
	return true
}

func TestRateLimiter_AllowsFirstCall(t *testing.T) {
	rl := newRateLimiter(100 * time.Millisecond)
	if !rl.Allow() {
		t.Fatal("first call should be allowed")
	}
}

func TestRateLimiter_BlocksSecondCall(t *testing.T) {
	rl := newRateLimiter(100 * time.Millisecond)
	rl.Allow()
	if rl.Allow() {
		t.Fatal("second call within window should be blocked")
	}
}

func TestRateLimiter_AllowsAfterWindow(t *testing.T) {
	rl := newRateLimiter(50 * time.Millisecond)
	rl.Allow()
	time.Sleep(60 * time.Millisecond)
	if !rl.Allow() {
		t.Fatal("call after window should be allowed")
	}
}

func TestRateLimiter_ConcurrentSafe(t *testing.T) {
	rl := newRateLimiter(10 * time.Millisecond)
	var wg sync.WaitGroup
	allowed := 0
	var mu sync.Mutex

	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if rl.Allow() {
				mu.Lock()
				allowed++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	if allowed > 2 {
		t.Fatalf("expected at most 2 allowed (10 concurrent with 10ms gap), got %d", allowed)
	}
}
