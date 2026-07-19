#!/usr/bin/env bash
# promptfoo custom provider: OpenRouter API (free model)
# Mucho más rápido que opencode run
set -euo pipefail

PROMPT="${1:-}"
if [ -z "$PROMPT" ]; then
    echo '{"error":"empty prompt"}'
    exit 1
fi

# Escape for JSON
ESCAPED=$(echo "$PROMPT" | python3 -c "
import sys, json
print(json.dumps(sys.stdin.read().strip()))
")

RESPONSE=$(python3 -c "
import httpx, json, os

try:
    r = httpx.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {os.environ[\"OPENROUTER_API_KEY\"]}',
            'Content-Type': 'application/json',
        },
        json={
            'model': 'qwen/qwen3-coder:free',
            'messages': [{'role': 'user', 'content': $ESCAPED}],
            'max_tokens': 500,
            'temperature': 0.1,
        },
        timeout=30,
    )
    data = r.json()
    if 'choices' in data and len(data['choices']) > 0:
        print(data['choices'][0]['message']['content'])
    else:
        print(json.dumps({'error': 'no choices', 'response': str(data)[:500]}))
except Exception as e:
    print(json.dumps({'error': str(e)}))
" 2>/dev/null)

# If the response is already JSON, pass through
if echo "$RESPONSE" | python3 -c "import sys,json;json.loads(sys.stdin.read())" 2>/dev/null; then
    echo "$RESPONSE"
else
    CLEAN=$(echo "$RESPONSE" | tr '\n' ' ' | sed 's/"/\\"/g')
    echo "{\"output\": \"$CLEAN\"}"
fi
