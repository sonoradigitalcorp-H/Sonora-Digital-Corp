#!/bin/bash
# SDD: Create specification for new feature
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

SPEC_DIR="sonora-digital-corp/docs/specs"
mkdir -p "$SPEC_DIR"

SPEC_FILE="$SPEC_DIR/${FEATURE_NAME}.md"

cat > "$SPEC_FILE" << EOF
# Specification: $FEATURE_NAME

## Overview
Brief description of the feature.

## Requirements
### Functional Requirements
- [ ] REQ-001: Description
- [ ] REQ-002: Description

### Non-Functional Requirements
- [ ] NFR-001: Performance
- [ ] NFR-002: Security
- [ ] NFR-003: Scalability

## Acceptance Criteria
- [ ] AC-001: Given... When... Then...
- [ ] AC-002: Given... When... Then...

## Technical Design
### Architecture
- Component diagram
- Data flow

### API Contract
\`\`\`yaml
openapi: 3.0.0
paths:
  /api/v1/$FEATURE_NAME:
    get:
      summary: Get $FEATURE_NAME
      responses:
        '200':
          description: Success
\`\`\`

### Database Schema
\`\`\`sql
CREATE TABLE $FEATURE_NAME (
  id UUID PRIMARY KEY,
  created_at TIMESTAMP DEFAULT NOW()
);
\`\`\`

## Test Plan
### Unit Tests
- [ ] Test case 1
- [ ] Test case 2

### Integration Tests
- [ ] Test case 1

### E2E Tests
- [ ] Test case 1

## Implementation Tasks
- [ ] Task 1
- [ ] Task 2

## Rollout Plan
- [ ] Staging
- [ ] Production
EOF

echo "Specification created: $SPEC_FILE"
echo "Edit the spec, then run: opencode run sdd:impl $FEATURE_NAME"