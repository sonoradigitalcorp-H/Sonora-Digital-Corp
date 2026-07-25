package orchestrator

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"path/filepath"
	"runtime"
)

// Loaded from Python TenantResolver via subprocess
type TenantContext struct {
	TenantID         string   `json:"tenant_id"`
	DisplayName      string   `json:"display_name"`
	Prompt           string   `json:"prompt"`
	AllowedTools     []string `json:"allowed_tools"`
	BlockedTools     []string `json:"blocked_tools"`
	QdrantCollection string   `json:"qdrant_collection"`
	Neo4jDatabase    string   `json:"neo4j_database"`
	DefaultModel     string   `json:"default_model"`
}

// TenantConfigFromID loads tenant config from the Python TenantResolver.
//
// It runs the resolver as a subprocess and parses JSON output.
// In production, this should be replaced with a direct Go implementation
// or an in-memory cache updated by the Python side.
func TenantConfigFromID(tenantID string) (*TenantContext, error) {
	_, filename, _, _ := runtime.Caller(0)
	repoRoot := filepath.Dir(filepath.Dir(filepath.Dir(filename)))

	script := fmt.Sprintf(`
import sys, json
sys.path.insert(0, %q)
from core.tenants.resolver import TenantResolver
r = TenantResolver()
ctx = r.load(%q)
print(json.dumps({
    "tenant_id": ctx.tenant_id,
    "display_name": ctx.display_name,
    "prompt": ctx.prompt,
    "allowed_tools": ctx.allowed_tools,
    "blocked_tools": ctx.blocked_tools,
    "qdrant_collection": ctx.qdrant_collection,
    "neo4j_database": ctx.neo4j_database,
    "default_model": ctx.config.get("default_model", ""),
}))
`, repoRoot, tenantID)

	cmd := exec.Command("python3", "-c", script)
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("tenant resolver: %w\n%s", err, string(output))
	}

	var ctx TenantContext
	if err := json.Unmarshal(output, &ctx); err != nil {
		return nil, fmt.Errorf("tenant resolver parse: %w", err)
	}
	return &ctx, nil
}

// IsToolAllowed checks if a tool is permitted for a tenant context.
func (tc *TenantContext) IsToolAllowed(toolName string) bool {
	if len(tc.AllowedTools) > 0 {
		found := false
		for _, t := range tc.AllowedTools {
			if t == toolName {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}
	for _, t := range tc.BlockedTools {
		if t == toolName {
			return false
		}
	}
	return true
}
