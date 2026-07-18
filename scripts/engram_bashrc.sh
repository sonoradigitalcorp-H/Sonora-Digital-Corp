#!/bin/bash
# Engram Auto-Capture Bash Hooks
# Source this file from ~/.bashrc:  source /path/to/scripts/engram_bashrc.sh
#
# FR-01: Auto-captura de comandos Bash via DEBUG trap + PROMPT_COMMAND
# FR-02: Snapshot de env al iniciar sesión
# FR-03: Snapshot de git después de ciertos comandos

ENGAM_AUTOCAPTURE="${BASH_SOURCE[0]%/*}/engram_autocapture.py"
ENGRAM_SESSION_ID="session_$(date +%s)_$$"
ENGRAM_LAST_COMMAND=""
ENGRAM_LAST_EXIT=0
ENGRAM_RATE_LIMIT=30
ENGRAM_RATE_COUNTER=0
ENGRAM_RATE_WINDOW=$(date +%s)

_engram_should_capture() {
    local cmd="$1"
    local readonly_commands="^ls |^cat |^grep |^pwd |^cd |^echo |^head |^tail |^less |^more |^wc |^which |^type |^help |^man "
    for pattern in $readonly_commands; do
        if [[ "$cmd" =~ $pattern ]]; then
            return 1
        fi
    done
    local relevant="^(git |npm |pip |docker |kubectl |make |rsync |scp |ssh |wacli |engram |python |python3 |node |npx |yarn |bun |go |cargo |systemctl |journalctl |helm |terraform |ansible |curl |psql |redis-cli )"
    if [[ "$cmd" =~ $relevant ]]; then
        return 0
    fi
    return 1
}

_engram_rate_ok() {
    local now
    now=$(date +%s)
    if (( now - ENGRAM_RATE_WINDOW >= 60 )); then
        ENGRAM_RATE_COUNTER=0
        ENGRAM_RATE_WINDOW=$now
    fi
    if (( ENGRAM_RATE_COUNTER >= ENGRAM_RATE_LIMIT )); then
        return 1
    fi
    ((ENGRAM_RATE_COUNTER++))
    return 0
}

_engram_capture_command() {
    local exit_code=$?
    local cmd
    cmd=$(history 1 | sed 's/^[ ]*[0-9]*[ ]*//')
    ENGRAM_LAST_EXIT=$exit_code
    ENGRAM_LAST_COMMAND="$cmd"
    if [ -z "$cmd" ]; then
        return
    fi
    if ! _engram_should_capture "$cmd"; then
        return
    fi
    if ! _engram_rate_ok; then
        return
    fi
    python3 "$ENGAM_AUTOCAPTURE" --capture-command "$cmd" --exit-code "$exit_code" --cwd "$PWD" --session-id "$ENGRAM_SESSION_ID" 2>/dev/null &
}

_engram_snapshot_env() {
    python3 "$ENGAM_AUTOCAPTURE" --snapshot env 2>/dev/null &
}

_engram_snapshot_git() {
    if [ -d "$PWD/.git" ]; then
        python3 "$ENGAM_AUTOCAPTURE" --snapshot git 2>/dev/null &
    fi
}

_engram_snapshot_processes() {
    python3 "$ENGAM_AUTOCAPTURE" --snapshot processes 2>/dev/null &
}

# ─── Hooks ──────────────────────────────────────────────────────────────────

# Capture after each command via PROMPT_COMMAND
if [ -z "${PROMPT_COMMAND_ENGAM:-}" ]; then
    PROMPT_COMMAND_ENGAM="_engram_capture_command"
fi
if [ -z "$PROMPT_COMMAND" ]; then
    PROMPT_COMMAND="$PROMPT_COMMAND_ENGAM"
else
    PROMPT_COMMAND="$PROMPT_COMMAND_ENGAM; $PROMPT_COMMAND"
fi

# Snapshot env at session start
_engram_snapshot_env

# Hook into git commands via bash-preexec or simple alias
# This runs before each command (DEBUG trap alternative)
# Actually we use PROMPT_COMMAND above which runs AFTER each command

echo "[engram] Auto-capture active — session: $ENGRAM_SESSION_ID"
