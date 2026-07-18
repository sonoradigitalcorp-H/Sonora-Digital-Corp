import subprocess, json

def ask(prompt, max_tokens=30):
    """Uses opencode run with DeepSeek V4 Flash for fast inference."""
    full_msg = prompt[:2000]
    try:
        r = subprocess.run(
            ["opencode", "run", full_msg],
            capture_output=True, text=True, timeout=180
        )
        out = r.stdout.strip()
        return out if out else "[ERROR: empty response]"
    except Exception as e:
        return f"[ERROR: {e}]"
