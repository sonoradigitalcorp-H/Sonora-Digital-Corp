package memory

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type Config struct {
	URL   string
	User  string
	Pass  string
}

type Lead struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Phone     string    `json:"phone"`
	Score     string    `json:"score"`
	History   []Entry   `json:"history"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type Entry struct {
	Timestamp  time.Time `json:"timestamp"`
	Type       string    `json:"type"`
	Summary    string    `json:"summary"`
	Transcript string    `json:"transcript,omitempty"`
	Duration   int       `json:"duration_seconds"`
	Tokens     int       `json:"tokens,omitempty"`
	Objective  string    `json:"objective,omitempty"`
}

func query(cfg Config, cypher string, params map[string]any) (string, error) {
	body := map[string]any{
		"statements": []map[string]any{
			{"statement": cypher, "parameters": params},
		},
	}
	b, _ := json.Marshal(body)

	req, err := http.NewRequest("POST", cfg.URL+"/db/neo4j/tx/commit", bytes.NewReader(b))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")
	req.SetBasicAuth(cfg.User, cfg.Pass)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var result bytes.Buffer
	result.ReadFrom(resp.Body)
	return result.String(), nil
}

func SaveCall(cfg Config, lead Lead, entry Entry) error {
	cypher := `
MERGE (l:Lead {id: $id})
ON CREATE SET l.name = $name, l.phone = $phone, l.score = $score, l.created_at = $created, l.updated_at = $updated
ON MATCH SET l.updated_at = $updated, l.name = $name
WITH l
CREATE (c:Call {id: $call_id, timestamp: $ts, type: $type, summary: $summary, duration: $duration, objective: $objective})
MERGE (l)-[:HAS_CALL]->(c)
SET l.score = $score
`
	_, err := query(cfg, cypher, map[string]any{
		"id": lead.ID, "name": lead.Name, "phone": lead.Phone,
		"score": lead.Score, "created": lead.CreatedAt.Format(time.RFC3339),
		"updated": time.Now().Format(time.RFC3339),
		"call_id": fmt.Sprintf("%s-%d", lead.ID, time.Now().Unix()),
		"ts": entry.Timestamp.Format(time.RFC3339),
		"type": entry.Type, "summary": entry.Summary,
		"duration": entry.Duration, "objective": entry.Objective,
	})
	return err
}

func GetLead(cfg Config, id string) (*Lead, error) {
	cypher := "MATCH (l:Lead {id: $id}) RETURN l"
	result, err := query(cfg, cypher, map[string]any{"id": id})
	if err != nil {
		return nil, err
	}
	_ = result
	return &Lead{ID: id}, nil
}
