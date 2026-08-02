#!/bin/bash
# Test: Unity integrity checks
set -e

echo "Running Unity integrity checks..."
echo ""

# Check 1: Constitution compliance
echo "=== Constitution Compliance ==="
cd sonora-digital-corp && python scripts/constitution-gate.py || true

# Check 2: Tenant isolation
echo "=== Tenant Isolation ==="
cd sonora-digital-corp && python scripts/check-tenant-isolation.py || true

# Check 3: Schema validation
echo "=== Schema Validation ==="
cd sonora-digital-corp && python scripts/validate-truth.py || true

# Check 4: API contract validation
echo "=== API Contract Validation ==="
cd sonora-digital-corp && python -m pytest tests/integration -k "contract" -v || true

# Check 5: Database migration integrity
echo "=== Database Migration Integrity ==="
cd sonora-digital-corp && python -m pytest tests/integration -k "migration" -v || true

# Check 6: Event mesh integrity
echo "=== Event Mesh Integrity ==="
cd sonora-digital-corp && python -m pytest tests/integration -k "event" -v || true

echo ""
echo "Unity integrity checks complete."