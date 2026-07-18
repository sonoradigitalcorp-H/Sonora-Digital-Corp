import subprocess
def ask(text: str) -> str:
    try:
        r = subprocess.run(["ollama", "run", "llama3.2:3b"], input=text, capture_output=True, text=True, timeout=120)
        out = r.stdout.strip()
        return out if out else "[ERROR: empty]"
    except subprocess.TimeoutExpired:
        return "[ERROR: timeout]"
    except Exception as e:
        return f"[ERROR: {e}]"
