package orchestrator

import (
	"io"
	"sync"
)

type mockCall struct {
	mu      sync.Mutex
	onReady func()
	onEnd   func(string)
	player  interface{ Play(source AudioSource); Stop(); OnFinish(fn func()) }
	sink    AudioSink
	ready   bool
	ended   bool
}

type mockPlayer struct {
	mu       sync.Mutex
	source   AudioSource
	onFinish func()
	playing  bool
}

type mockSink struct {
	mu         sync.Mutex
	writeCount int
}

func newMockCall() *mockCall {
	return &mockCall{}
}

func (c *mockCall) OnReady(fn func()) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.onReady = fn
	if c.ready && fn != nil {
		go fn()
	}
}

func (c *mockCall) OnEnd(fn func(string)) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.onEnd = fn
}

func (c *mockCall) Subscribe(p interface{ Play(source AudioSource); Stop(); OnFinish(fn func()) }) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.player = p
}

func (c *mockCall) Receive(sink AudioSink) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.sink = sink
}

func (c *mockCall) Hangup() error {
	c.mu.Lock()
	c.ended = true
	fn := c.onEnd
	c.mu.Unlock()
	if fn != nil {
		go fn("hangup")
	}
	return nil
}

func (c *mockCall) answer() {
	c.mu.Lock()
	c.ready = true
	fn := c.onReady
	c.mu.Unlock()
	if fn != nil {
		go fn()
	}
}

func (p *mockPlayer) Play(src AudioSource) {
	p.mu.Lock()
	p.source = src
	p.playing = true
	p.mu.Unlock()
	go func() {
		for {
			_, err := src.ReadFrame()
			if err == io.EOF {
				break
			}
			if err != nil {
				break
			}
		}
		p.mu.Lock()
		p.playing = false
		fn := p.onFinish
		p.mu.Unlock()
		if fn != nil {
			fn()
		}
	}()
}

func (p *mockPlayer) Stop() {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.playing = false
}

func (p *mockPlayer) OnFinish(fn func()) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.onFinish = fn
}

func (s *mockSink) WriteFrame(_ []float32) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.writeCount++
	return nil
}

func (s *mockSink) Close() error {
	return nil
}
