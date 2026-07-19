# sdk-python — Sonora Python SDK Gateway Access

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-SDK-001

---

## 1. Business Objective

Provide unified gateway access from all Python scripts using the Sonora Python SDK (mcp/sdk/sonora_client.py) for gateway access, health checks, and tool calls.

## 2. Inputs (Gherkin)

```gherkin
Given Python 3.10+ environment is available
When sonora_client.py is importable from mcp/sdk/
And gateway endpoint is configured in environment
```

## 3. Outputs (Gherkin)

```gherkin
Then SDK client connects to gateway
And tool() calls return structured results
And health() returns gateway status
And capabilities() lists available functions
And skills() enumerates registered skills
```

## 4. Events

```
Events:
- sdk:tool:called: SDK tool execution completed
- sdk:auth:refreshed: authentication token rotated
```

## 5. Dependencies

```
Dependencies:
- SonoraSDK class: mcp/sdk/sonora_client.py
- Gateway: running and accessible
- Python: 3.10+ with httpx
```

## 6. Tools

```
Tools:
- SonoraSDK: client class wrapping gateway API
- tool(): execute a named tool on the gateway
- health(): check gateway health status
- capabilities(): list available capabilities
- skills(): list registered skills
```

## 7. Policies

```
Policies:
- All gateway access must go through the SDK, never raw HTTP
- Auth tokens must be refreshed before expiry
- SDK calls must include timeout and retry logic
- Credentials must never be logged or printed
```

## 8. Success Metrics

```gherkin
Success Metrics:
- call_success_rate: Given SDK calls in period When completed Then rate
  Target: > 99%
- auth_refresh_time: Given token expiry When refreshed Then milliseconds
  Target: < 500 ms
```

## 9. Failure Conditions

```
Failure Conditions:
- Connection timeout: gateway unreachable (retry 3x with backoff)
- Auth failure: token expired without refresh (re-authenticate)
- SDK import error: sonora_client.py missing or corrupted
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If connection fails → retry with exponential backoff (3 attempts)
2. If auth fails → refresh token, retry original call
3. If import fails → verify PYTHONPATH includes mcp/sdk/
4. Log all attempts to state/logs/skills/sdk-python.log
```

## 11. Business Value

```
Business Value: Unified gateway access from all Python scripts. Eliminates ad-hoc HTTP calls.
```

## 12. Parent OS

```
Parent OS: Dev
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: sdk:tool:called, sdk:auth:refreshed
- Logs: state/logs/skills/sdk-python.log
```
