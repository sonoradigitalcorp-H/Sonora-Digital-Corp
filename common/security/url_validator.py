"""URL Validator — SSRF Protection for SDC MCP Tools.

Validates URLs against SSRF attacks before passing to external services.
Ensures HTTPS, checks against private IP ranges, validates domains.

Usage:
    from common.security.url_validator import validate_url, validate_urls
    
    result = validate_url("http://localhost:6333/secret")
    if not result.valid:
        log.warning(f"SSRF blocked: {result.reason}")
"""

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"https"}
BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "[::1]", "::1", "metadata.google.internal", "169.254.169.254"}
MAX_URL_LENGTH = 2048
ALLOWED_DOMAINS = []  # Empty = allow all public HTTPS (block only private/internal)


@dataclass
class URLValidationResult:
    valid: bool = True
    reason: str = ""
    scheme: str = ""
    hostname: str = ""
    port: int = 0
    normalized_url: str = ""


def _is_private_ip(hostname: str) -> bool:
    """Check if hostname resolves to a private IP range."""
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast
    except ValueError:
        return False


def validate_url(url: str) -> URLValidationResult:
    """Validate a single URL against SSRF attacks."""
    result = URLValidationResult()
    
    if not url:
        result.valid = False
        result.reason = "Empty URL"
        return result
    
    if len(url) > MAX_URL_LENGTH:
        result.valid = False
        result.reason = f"URL exceeds maximum length ({len(url)} > {MAX_URL_LENGTH})"
        return result
    
    try:
        parsed = urlparse(url)
    except Exception as e:
        result.valid = False
        result.reason = f"URL parse error: {e}"
        return result
    
    result.scheme = parsed.scheme
    result.hostname = parsed.hostname or ""
    result.port = parsed.port or 0
    
    # Check scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        result.valid = False
        result.reason = f"Scheme '{parsed.scheme}' not allowed. Only HTTPS supported."
        return result
    
    # Check blocked hosts
    if parsed.hostname in BLOCKED_HOSTS:
        result.valid = False
        result.reason = f"Hostname '{parsed.hostname}' is blocked (internal service)"
        return result
    
    # Check private IPs
    if _is_private_ip(parsed.hostname):
        result.valid = False
        result.reason = f"IP '{parsed.hostname}' is a private/internal IP range"
        return result
    
    # Check for IP in hostname (IPv4/IPv6)
    ip_match = re.match(r'^(\d{1,3}\.){3}\d{1,3}$', parsed.hostname)
    if ip_match:
        parts = parsed.hostname.split('.')
        if all(0 <= int(p) <= 255 for p in parts):
            if _is_private_ip(parsed.hostname):
                result.valid = False
                result.reason = f"IP '{parsed.hostname}' is in private range"
                return result
    
    # Domain allowlist check (if configured)
    if ALLOWED_DOMAINS:
        hostname_lower = parsed.hostname.lower()
        allowed = any(
            hostname_lower == domain or hostname_lower.endswith(f".{domain}")
            for domain in ALLOWED_DOMAINS
        )
        if not allowed:
            result.valid = False
            result.reason = f"Domain '{parsed.hostname}' not in allowlist"
            return result
    
    # Basic URL format validation
    if not parsed.hostname or not parsed.scheme:
        result.valid = False
        result.reason = "Invalid URL format"
        return result
    
    result.normalized_url = url
    return result


def validate_urls(urls: list[str]) -> list[URLValidationResult]:
    """Validate a list of URLs."""
    return [validate_url(u) for u in urls]


def filter_valid_urls(urls: list[str]) -> list[str]:
    """Return only URLs that pass validation."""
    return [u for u in urls if validate_url(u).valid]


def filter_invalid_urls(urls: list[str]) -> list[str]:
    """Return URLs that FAIL validation."""
    return [u for u in urls if not validate_url(u).valid]
