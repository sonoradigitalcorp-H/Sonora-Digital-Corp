# SDC Debugging Skill

## Overview

Systematic debugging approach for Sonora Digital Corp projects.

## When to Use

- Tests are failing
- Application errors
- Performance issues
- Deployment problems

## Debugging Workflow

### Step 1: Understand the Error

```bash
# Read the error message carefully
# What is the error type?
# What is the error message?
# Where does it occur?
# When does it occur?
```

### Step 2: Search for Patterns

```bash
# Search engram for similar errors
# Check git log for similar fixes
# Look for known issues in AGENTS.md
```

### Step 3: Isolate the Problem

```bash
# Run specific test
PYTHONPATH=. python3 -m pytest tests/unit/test_specific.py -v

# Check logs
docker compose logs -f service_name

# Check environment
env | grep VARIABLE
```

### Step 4: Apply Fix

```bash
# Make minimal change
# Test the fix
# Verify no regressions
```

### Step 5: Document

```bash
# Save lesson to engram
# Update documentation if needed
# Commit with descriptive message
```

## Common Error Patterns

### Import Errors

```python
# Problem: ModuleNotFoundError
# Fix: Check PYTHONPATH
PYTHONPATH=. python3 -m pytest tests/

# Problem: ImportError
# Fix: Check __init__.py files
```

### Docker Errors

```bash
# Problem: Container won't start
docker compose logs service_name

# Problem: Port already in use
lsof -i :PORT
docker rm -f container_name

# Problem: Volume mount issues
# Fix: Check path exists, permissions correct
```

### Test Failures

```bash
# Problem: Test timeout
# Fix: Mock external services

# Problem: Flaky test
# Fix: Add proper setup/teardown

# Problem: Missing fixtures
# Fix: Add conftest.py
```

### Memory Issues

```bash
# Problem: OOM killed
# Fix: Increase memory limit or optimize code

# Problem: Memory leak
# Fix: Check for unclosed connections
```

### Performance Issues

```bash
# Problem: Slow queries
# Fix: Add indexes, optimize queries

# Problem: High latency
# Fix: Add caching, reduce polling intervals
```

## Environment-Specific Debugging

### Local Development

```bash
# Check services
docker ps -a

# Check logs
docker compose logs -f

# Restart services
docker compose restart

# Clean and rebuild
docker compose down
docker compose up -d
```

### CI/CD

```bash
# Check workflow logs
# Verify dependencies installed
# Check environment variables
# Verify secrets configured
```

### Production (VPS)

```bash
# SSH to VPS
ssh ubuntu@149.56.46.173

# Check services
docker ps -a --format 'table {{.Names}}\t{{.Status}}'
docker stats --no-stream

# Check logs
docker compose -f /home/ubuntu/sonora-digital-corp/infra/docker-compose.yml logs -f

# Restart if needed
docker compose restart service_name
```

## Debugging Tools

### Python Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use built-in
breakpoint()

# Print debug
import pprint; pprint.pprint(variable)
```

### Docker Debugging

```bash
# Enter container
docker exec -it container_name bash

# Check logs
docker logs container_name

# Check resources
docker stats
```

### Network Debugging

```bash
# Check connectivity
curl -v http://localhost:PORT/health

# Check ports
netstat -tlnp

# Check DNS
nslookup hostname
```

## Escalation Path

1. **Self-service**: Search engram, git log, documentation
2. **Local debugging**: Use pdb, logs, docker commands
3. **Ask for help**: Describe error, steps to reproduce, what you've tried
4. **Escalate**: Contact team lead with full context

## Prevention

### Code Quality
- Write tests first (TDD)
- Run linter before commit
- Use type hints
- Document complex logic

### Infrastructure
- Use pre-flight checks
- Monitor health endpoints
- Set up alerts
- Keep dependencies updated

### Process
- Follow SDD lifecycle
- Document decisions
- Review code before merge
- Test in staging first
