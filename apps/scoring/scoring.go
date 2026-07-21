package scoring

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type Result struct {
	Score     string `json:"score"`
	Summary   string `json:"summary"`
	NextStep  string `json:"next_step"`
	FollowUp  int    `json:"follow_up_days"`
}

func Analyze(apiKey, model, transcript string) (*Result, error) {
	prompt := fmt.Sprintf(`Analiza esta transcripción de llamada de ventas y clasifica el lead.

TRANSCRIPCIÓN:
%s

Responde en JSON:
{
  "score": "cold" | "warm" | "hot",
  "summary": "resumen de 1 línea",
  "next_step": "qué hacer después",
  "follow_up_days": días para follow-up (0 si hot, 3 si warm, 7 si cold)
}`, transcript)

	body := map[string]any{
		"model": model,
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
		"max_tokens": 200,
	}
	b, _ := json.Marshal(body)

	req, _ := http.NewRequest("POST", "https://openrouter.ai/api/v1/chat/completions", bytes.NewReader(b))
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("llm: %w", err)
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
		return nil, err
	}
	if len(result.Choices) == 0 {
		return nil, io.ErrUnexpectedEOF
	}

	content := result.Choices[0].Message.Content
	content = strings.TrimSpace(content)
	content = strings.TrimPrefix(content, "```json")
	content = strings.TrimPrefix(content, "```")
	content = strings.TrimSuffix(content, "```")

	var r Result
	if err := json.Unmarshal([]byte(content), &r); err != nil {
		return nil, fmt.Errorf("parse scoring: %w", err)
	}
	return &r, nil
}

func DurationString(d time.Duration) string {
	m := int(d.Minutes())
	s := int(d.Seconds()) % 60
	return fmt.Sprintf("%dm%ds", m, s)
}
