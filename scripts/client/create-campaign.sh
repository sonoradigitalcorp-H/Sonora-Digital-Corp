#!/bin/bash
# Client: Create marketing campaign
set -e

CLIENT="${1:-}"
CAMPAIGN_TYPE="${2:-general}"
if [ -z "$CLIENT" ]; then
  echo "Usage: $0 <client-name> [campaign-type]"
  echo "Campaign types: general, launch, seasonal, retargeting, brand-awareness"
  exit 1
fi

echo "Creating $CAMPAIGN_TYPE campaign for client: $CLIENT"

CAMPAIGN_DIR="sonora-digital-corp/tenants/$CLIENT/campaigns"
mkdir -p "$CAMPAIGN_DIR"

CAMPAIGN_FILE="$CAMPAIGN_DIR/${CAMPAIGN_TYPE}-$(date +%Y%m%d).md"

cat > "$CAMPAIGN_FILE" << EOF
# Campaign: $CAMPAIGN_TYPE for $CLIENT

## Objective
Define campaign objective here.

## Target Audience
- Primary:
- Secondary:

## Key Messages
1. Message 1
2. Message 2

## Channels
- [ ] Website/Landing Page
- [ ] Social Media
- [ ] Email Marketing
- [ ] Paid Ads
- [ ] WhatsApp/Telegram
- [ ] SEO/Content

## Timeline
- Start: $(date +%Y-%m-%d)
- End: 

## Budget
- Total:
- Allocation:

## KPIs
- [ ] KPI 1
- [ ] KPI 2

## Assets Needed
- [ ] Landing Page
- [ ] Ad Creatives
- [ ] Email Templates
- [ ] Social Posts

## Automation
- [ ] MCP: Social Media Posting
- [ ] MCP: Email Automation
- [ ] MCP: Analytics Tracking

## Approval
- [ ] Client Review
- [ ] Legal Review
- [ ] Launch Approval
EOF

echo "Campaign created: $CAMPAIGN_FILE"
echo "Edit the campaign, then deploy with: opencode run client:deploy-campaign $CLIENT $CAMPAIGN_TYPE"