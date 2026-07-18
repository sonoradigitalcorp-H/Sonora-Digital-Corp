package orchestrator

import (
	"context"
	"errors"
	"io"
	"testing"
	"time"
)

type errSource struct{}

func (e *errSource) ReadFrame() ([]float32, error) { return nil, io.EOF }
func (e *errSource) Close() error                  { return errors.New("close error") }

type errSink struct{}

func (e *errSink) WriteFrame(_ []float32) error { return errors.New("write error") }
func (e *errSink) Close() error                  { return errors.New("sink close error") }

func TestEngineRun_TTSFails(t *testing.T) {
	mc := newMockCall()
	mp := &mockPlayer{}
	ttsErr := errors.New("tts failed")
	ttsFn := func(text string) (AudioSource, error) { return nil, ttsErr }

	engine := New(Config{
		LeadName:    "Test",
		LeadID:      "fail-tts",
		Objective:   "test",
		TTSSourceFn: ttsFn,
		LLMFn:       newMockLLM,
	})

	errCh := make(chan error, 1)
	go func() { errCh <- engine.Run(context.Background(), mc, mp) }()

	mc.answer()
	time.Sleep(50 * time.Millisecond)
	engine.Stop()

	select {
	case err := <-errCh:
		if err != nil {
			t.Logf("engine returned (expected): %v", err)
		}
	case <-time.After(3 * time.Second):
		t.Fatal("timed out — engine likely deadlocked on TTS error")
	}
}

func TestEngineRun_LLMFails(t *testing.T) {
	mc := newMockCall()
	mp := &mockPlayer{}
	llmErr := errors.New("llm failed")
	llmFn := func(msgs []map[string]string) (string, error) { return "", llmErr }

	engine := New(Config{
		LeadName:    "Test",
		LeadID:      "fail-llm",
		Objective:   "test",
		TTSSourceFn: newMockSource,
		LLMFn:       llmFn,
	})

	errCh := make(chan error, 1)
	go func() { errCh <- engine.Run(context.Background(), mc, mp) }()

	mc.answer()
	time.Sleep(50 * time.Millisecond)
	engine.Stop()

	select {
	case err := <-errCh:
		if err != nil {
			t.Logf("engine returned (expected): %v", err)
		}
	case <-time.After(3 * time.Second):
		t.Fatal("timed out — engine likely deadlocked on LLM error")
	}
}

func TestSink_WriteCountMatches(t *testing.T) {
	s := &mockSink{}
	for i := 0; i < 100; i++ {
		f := make([]float32, 960)
		if err := s.WriteFrame(f); err != nil {
			t.Fatalf("WriteFrame: %v", err)
		}
	}
	if s.writeCount != 100 {
		t.Fatalf("expected 100 writes, got %d", s.writeCount)
	}
}

func TestPlayer_OnFinishCalled(t *testing.T) {
	p := &mockPlayer{}
	done := make(chan struct{}, 1)
	p.OnFinish(func() { done <- struct{}{} })
	p.Play(&mockSimpleSource{frames: 3})

	select {
	case <-done:
	case <-time.After(time.Second):
		t.Fatal("OnFinish not called after source EOF")
	}
}
