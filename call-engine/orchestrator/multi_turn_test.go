package orchestrator

import (
	"sync"
	"testing"
)

func TestLLMSequence_MultipleTurns(t *testing.T) {
	responses := []string{
		"Cuéntame más sobre lo que necesitas",
		"Entiendo, tenemos una solución para eso",
		"Claro, te explico cómo funciona",
		"El precio depende del volumen",
		"Te envío la propuesta por WhatsApp",
	}

	var mu sync.Mutex
	index := 0
	llmFn := func(msgs []map[string]string) (string, error) {
		mu.Lock()
		defer mu.Unlock()
		if index >= len(responses) {
			return "fin", nil
		}
		r := responses[index]
		index++
		return r, nil
	}

	history := []map[string]string{
		{"role": "system", "content": "test"},
	}

	for i, expected := range responses {
		resp, err := llmFn(history)
		if err != nil {
			t.Fatalf("turn %d LLM error: %v", i, err)
		}
		if resp != expected {
			t.Fatalf("turn %d: expected %q, got %q", i, expected, resp)
		}
		history = append(history, map[string]string{"role": "assistant", "content": resp})
		history = append(history, map[string]string{"role": "user", "content": "siguiente"})
	}

	mu.Lock()
	if index != len(responses) {
		t.Fatalf("expected %d LLM calls, got %d", len(responses), index)
	}
	mu.Unlock()
}

func TestLLMSequence_StopsAtLimit(t *testing.T) {
	limit := 3
	count := 0
	llmFn := func(msgs []map[string]string) (string, error) {
		count++
		if count > limit {
			return "STOP", nil
		}
		return "respuesta", nil
	}

	for i := 0; i < limit+2; i++ {
		resp, _ := llmFn(nil)
		if resp == "STOP" {
			break
		}
	}

	if count != limit+1 {
		t.Fatalf("expected %d LLM calls before STOP, got %d", limit+1, count)
	}
}

