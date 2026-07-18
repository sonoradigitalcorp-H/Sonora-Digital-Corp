package orchestrator

import (
	"context"
	"io"
	"testing"
	"time"
)

func newMockSource(text string) (AudioSource, error) {
	return &mockSimpleSource{frames: 1}, nil
}

func newMockLLM(messages []map[string]string) (string, error) {
	return "Entendido, te ayudo con eso. ¿Qué más necesitas?", nil
}

func TestEngineRun_AnswerAndHangup(t *testing.T) {
	mc := newMockCall()
	mp := &mockPlayer{}
	engine := New(Config{
		LeadName:    "Nathaly",
		LeadID:      "nathaly-test-1",
		Objective:   "ofrecer servicios",
		TTSSourceFn: newMockSource,
		LLMFn:       newMockLLM,
	})

	errCh := make(chan error, 1)
	go func() {
		errCh <- engine.Run(context.Background(), mc, mp)
	}()

	mc.answer()
	time.Sleep(50 * time.Millisecond)
	mc.Hangup()
	engine.Stop()

	select {
	case err := <-errCh:
		if err != nil {
			t.Logf("engine returned: %v", err)
		}
	case <-time.After(3 * time.Second):
		t.Fatal("timed out")
	}
}

func TestEngineRun_HangupBeforeAnswer(t *testing.T) {
	mc := newMockCall()
	mp := &mockPlayer{}
	engine := New(Config{
		LeadName:    "Test",
		LeadID:      "test-2",
		Objective:   "test",
		TTSSourceFn: newMockSource,
		LLMFn:       newMockLLM,
	})

	errCh := make(chan error, 1)
	ctx := context.Background()
	go func() {
		errCh <- engine.Run(ctx, mc, mp)
	}()

	mc.Hangup()
	engine.Stop()

	select {
	case err := <-errCh:
		if err != nil {
			t.Logf("engine returned (expected): %v", err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("timed out")
	}
}

func TestMockCall_AnswerAndHangup(t *testing.T) {
	c := newMockCall()
	ready := make(chan struct{}, 1)
	ended := make(chan string, 1)

	c.OnReady(func() { ready <- struct{}{} })
	c.OnEnd(func(r string) { ended <- r })

	c.answer()

	select {
	case <-ready:
	case <-time.After(time.Second):
		t.Fatal("ready not called")
	}

	c.Hangup()

	select {
	case r := <-ended:
		if r != "hangup" {
			t.Fatalf("expected 'hangup', got %q", r)
		}
	case <-time.After(time.Second):
		t.Fatal("end not called")
	}
}

func TestMockSink_WriteCount(t *testing.T) {
	s := &mockSink{}
	frame := make([]float32, 960)
	for i := 0; i < 10; i++ {
		if err := s.WriteFrame(frame); err != nil {
			t.Fatalf("WriteFrame: %v", err)
		}
	}
	if s.writeCount != 10 {
		t.Fatalf("expected 10 writes, got %d", s.writeCount)
	}
}

func TestMockPlayer_PlayAndFinish(t *testing.T) {
	p := &mockPlayer{}
	finished := make(chan struct{}, 1)
	p.OnFinish(func() { finished <- struct{}{} })

	src := &mockSimpleSource{frames: 3}
	p.Play(src)

	select {
	case <-finished:
	case <-time.After(time.Second):
		t.Fatal("OnFinish not called")
	}
}

type mockSimpleSource struct {
	frames int
	pos    int
}

func (s *mockSimpleSource) ReadFrame() ([]float32, error) {
	s.pos++
	if s.pos > s.frames {
		return nil, io.EOF
	}
	return make([]float32, 960), nil
}

func (s *mockSimpleSource) Close() error {
	return nil
}
