package orchestrator

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"

	meow "github.com/purpshell/meowcaller"
	"github.com/sonoradigitalcorp/call-engine/stt"
	"github.com/sonoradigitalcorp/call-engine/tts"
)

type AudioSource = meow.AudioSource
type AudioSink = meow.AudioSink

type Config struct {
	OpenRouterKey string
	Model         string
	LeadName      string
	LeadID        string
	Objective     string
	LeadContext   string
	Tone          string
	TmpDir        string
	TTSSourceFn   func(text string) (AudioSource, error)
	LLMFn         func(messages []map[string]string) (string, error)
}

type CallInterface interface {
	OnReady(fn func())
	OnEnd(fn func(string))
	Subscribe(p interface{ Play(source AudioSource); Stop(); OnFinish(fn func()) })
	Receive(sink AudioSink)
	Hangup() error
}

type Engine struct {
	cfg  Config
	mu   sync.Mutex
	done chan struct{}
}

func New(cfg Config) *Engine {
	return &Engine{cfg: cfg, done: make(chan struct{})}
}

func (e *Engine) Run(ctx context.Context, call CallInterface, player interface{ Play(source AudioSource); Stop(); OnFinish(fn func()) }) error {
	log := func(msg string) {
		fmt.Printf("[call] %s\n", msg)
	}

	systemPrompt := fmt.Sprintf(`Eres un agente de ventas de Sonora Digital Corp.
LLAMAS a: %s
OBJETIVO: %s
CONTEXTO: %s
TONO: %s

Reglas:
- Escucha más de lo que hablas
- No interrumpas
- Si hay objeción: valida → entiende → responde
- Al final, deja claro el próximo paso
- NUNCA mientas sobre capacidades
- Responde en español, directo, natural

LLAMADA INICIADA. Saluda al lead y comienza la conversación.`,
		e.cfg.LeadName, e.cfg.Objective, e.cfg.LeadContext, e.cfg.Tone)

	var messages []map[string]string
	messages = append(messages, map[string]string{"role": "system", "content": systemPrompt})

	onText := func(text string) {
		log(">> " + text)
		messages = append(messages, map[string]string{"role": "user", "content": text})

		response, err := e.askLLM(messages)
		if err != nil {
			log("LLM error: " + err.Error())
			return
		}
		log("<< " + response)
		messages = append(messages, map[string]string{"role": "assistant", "content": response})

		var source AudioSource
		if e.cfg.TTSSourceFn != nil {
			source, err = e.cfg.TTSSourceFn(response)
		} else {
			source, err = tts.NewEdgeSource(response, e.cfg.TmpDir)
		}
		if err != nil {
			log("TTS error: " + err.Error())
			return
		}
		player.Play(source)
	}

	sink := stt.NewWhisperSink(e.cfg.TmpDir, onText)
	call.Receive(sink)

	firstMsg := fmt.Sprintf("Hola %s, soy de Sonora Digital Corp. Te llamo porque %s. ¿Te parece bien si te cuento un poco?", e.cfg.LeadName, e.cfg.Objective)
	var source AudioSource
	var err error
	if e.cfg.TTSSourceFn != nil {
		source, err = e.cfg.TTSSourceFn(firstMsg)
	} else {
		source, err = tts.NewEdgeSource(firstMsg, e.cfg.TmpDir)
	}
	if err != nil {
		return fmt.Errorf("initial TTS: %w", err)
	}
	call.Subscribe(player)
	player.Play(source)
	log("< " + firstMsg)

	<-e.done
	sink.Close()
	return nil
}

func (e *Engine) Stop() {
	select {
	case <-e.done:
	default:
		close(e.done)
	}
}

func (e *Engine) askLLM(messages []map[string]string) (string, error) {
	if e.cfg.LLMFn != nil {
		return e.cfg.LLMFn(messages)
	}
	body := map[string]any{
		"model": e.cfg.Model,
		"messages": messages,
		"max_tokens": 300,
		"temperature": 0.7,
	}
	b, _ := json.Marshal(body)

	req, err := http.NewRequest("POST", "https://openrouter.ai/api/v1/chat/completions", bytes.NewReader(b))
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+e.cfg.OpenRouterKey)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("HTTP-Referer", "https://sonoradigitalcorp.com")

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var result struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}
	if len(result.Choices) == 0 {
		return "", io.ErrUnexpectedEOF
	}
	return result.Choices[0].Message.Content, nil
}
