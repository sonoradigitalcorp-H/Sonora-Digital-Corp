"""FFmpeg Sanitizer — Prevent filter injection attacks via FFmpeg parameters.

Sanitizes user-provided text before interpolation into FFmpeg filter strings.
Prevents: textfile= file reads, filter injection, special character exploits.

Usage:
    from common.security.ffmpeg_sanitizer import sanitize_watermark, sanitize_filter_arg
    
    safe_text = sanitize_watermark(user_provided_text)
"""

import re
from dataclasses import dataclass

MAX_WATERMARK_LENGTH = 100
ALLOWED_WATERMARK_CHARS = re.compile(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-_\.\,\!\?\(\)\@\#\$\%\&\*\+]+$')

BLOCKED_FFMPEG_DIRECTIVES = sorted({
    "textfile", "loadfont", "fontfile", "start_number",
    "codec", "filter", "lavfi", "movie", "concat",
}, key=len, reverse=True)


@dataclass
class SanitizeResult:
    safe: bool = True
    sanitized: str = ""
    original: str = ""
    reason: str = ""


def sanitize_watermark(text: str) -> SanitizeResult:
    """Sanitize user-provided watermark text for FFmpeg drawtext filter."""
    result = SanitizeResult(original=text)
    
    if not text:
        result.safe = True
        result.sanitized = ""
        return result
    
    # Length check
    if len(text) > MAX_WATERMARK_LENGTH:
        text = text[:MAX_WATERMARK_LENGTH]
        result.reason = f"Truncated to {MAX_WATERMARK_LENGTH} chars"
    
    # Block FFmpeg directives
    text_lower = text.lower()
    for directive in BLOCKED_FFMPEG_DIRECTIVES:
        if directive in text_lower:
            result.safe = False
            result.reason = f"Blocked FFmpeg directive: '{directive}'"
            result.sanitized = text.replace(directive, f"[blocked:{directive}]")
            return result
    
    # Remove single quotes (ffmpeg filter syntax breaker)
    text = text.replace("'", "’")
    
    # Remove double quotes
    text = text.replace('"', "''")
    
    # Remove colon (ffmpeg filter separator)
    text = text.replace(":", " ")
    
    # Remove backslash
    text = text.replace("\\", "")
    
    # Remove brackets (filter chain syntax)
    text = text.replace("[", "(").replace("]", ")")
    
    # Remove semicolon (filter chain separator)
    text = text.replace(";", ",")
    
    # Remove comma at start/end (filter argument separator)
    text = text.strip(",")
    
    # Final character validation
    if not ALLOWED_WATERMARK_CHARS.match(text):
        # Remove any non-allowed characters
        text = ''.join(c for c in text if ALLOWED_WATERMARK_CHARS.match(c) or c in (' ', 'á', 'é', 'í', 'ó', 'ú', 'ñ'))
    
    result.sanitized = text
    return result


def sanitize_filter_arg(arg: str) -> str:
    """Sanitize a general FFmpeg filter argument."""
    if not arg:
        return arg
    
    # Remove potential injection characters
    arg = arg.replace("'", "’")
    arg = arg.replace('"', "''")
    arg = arg.replace(":", " ")
    arg = arg.replace("\\", "")
    arg = arg.replace(";", ",")
    arg = arg.replace("[", "(").replace("]", ")")
    arg = arg.replace("$", "")
    arg = arg.replace("`", "")
    
    return arg.strip()


def validate_file_path(path: str) -> bool:
    """Validate that a file path is safe for FFmpeg operations."""
    if not path:
        return False
    # Path must start with /tmp/ or current directory
    allowed_prefixes = ("/tmp/", "./", "../output")
    if not any(path.startswith(p) for p in allowed_prefixes):
        return False
    # No path traversal
    if ".." in path.split("/"):
        return False
    # No special characters
    if re.search(r"[;'\"$`!#&()\[\]{}|<>]", path):
        return False
    return True
