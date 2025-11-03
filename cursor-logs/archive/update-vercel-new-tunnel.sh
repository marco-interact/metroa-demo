#!/bin/bash
set -e

export VERCEL_TOKEN="ycSDrQ8tYp4L6Z0qFfOK4igb"
export VERCEL_ORG_ID="team_PWckdPO4Vl3C1PWOA9qs9DrI"
export VERCEL_PROJECT_ID="prj_pWPdNcXNWyzQaaDysmBGMiU15AB1"
TUNNEL_URL="https://defines-pocket-doc-qualify.trycloudflare.com"

echo "🔧 Updating Vercel with new tunnel URL..."
echo "New Tunnel: $TUNNEL_URL"

# Get existing env var ID
ENV_ID=$(curl -s "https://api.vercel.com/v9/projects/$VERCEL_PROJECT_ID/env?teamId=$VERCEL_ORG_ID" \
  -H "Authorization: Bearer $VERCEL_TOKEN" | \
  jq -r '.envs[] | select(.key == "NEXT_PUBLIC_API_URL" and (.target[] | contains("production"))) | .id')

# Delete old
if [ -n "$ENV_ID" ]; then
  curl -s -X DELETE \
    "https://api.vercel.com/v9/projects/$VERCEL_PROJECT_ID/env/$ENV_ID?teamId=$VERCEL_ORG_ID" \
    -H "Authorization: Bearer $VERCEL_TOKEN" > /dev/null
fi

# Add new
curl -s -X POST \
  "https://api.vercel.com/v10/projects/$VERCEL_PROJECT_ID/env?teamId=$VERCEL_ORG_ID" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"key\": \"NEXT_PUBLIC_API_URL\",
    \"value\": \"$TUNNEL_URL\",
    \"target\": [\"production\", \"preview\"],
    \"type\": \"plain\"
  }" | jq -r '"✅ Updated: " + .value'

# Redeploy
curl -s -X POST \
  "https://api.vercel.com/v13/deployments?teamId=$VERCEL_ORG_ID" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$VERCEL_PROJECT_ID\",
    \"project\": \"$VERCEL_PROJECT_ID\",
    \"target\": \"production\",
    \"forceNew\": true
  }" > /dev/null

echo "✅ Vercel updated and redeploying!"
