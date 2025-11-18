#!/bin/bash
################################################################################
# Frontend Update Script for New Pod
# Updates Vercel frontend to point to new backend pod
# Pod: 8pexe48luksdw3
################################################################################

set -e

POD_ID="8pexe48luksdw3"
PUBLIC_URL="https://${POD_ID}-8888.proxy.runpod.net"
PROJECT_DIR="/Users/marco.aurelio/Desktop/metroa-demo"

echo "=================================================="
echo "🌐 Updating Frontend for New Pod"
echo "=================================================="
echo ""
echo "📋 Configuration:"
echo "   • Pod ID: $POD_ID"
echo "   • Backend URL: $PUBLIC_URL"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() { echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ${NC}  $1"; }

# Check if we're in the right directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Project directory not found: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

################################################################################
# Step 1: Update .env.production
################################################################################

print_step "Step 1/3: Updating .env.production..."

cat > .env.production << EOF
NEXT_PUBLIC_API_URL="$PUBLIC_URL"
EOF

print_info "✅ Updated .env.production"
print_info "   NEXT_PUBLIC_API_URL=\"$PUBLIC_URL\""

################################################################################
# Step 2: Verify Backend is Running
################################################################################

print_step "Step 2/3: Verifying backend is running..."

if curl -s "$PUBLIC_URL/health" > /dev/null; then
    print_info "✅ Backend is responding!"
    echo ""
    echo "Backend Health Check:"
    curl -s "$PUBLIC_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$PUBLIC_URL/health"
    echo ""
else
    echo "⚠️  Warning: Backend not responding at $PUBLIC_URL"
    echo "   Make sure backend is running on the pod first!"
    echo ""
fi

################################################################################
# Step 3: Deploy to Vercel
################################################################################

print_step "Step 3/3: Deploying to Vercel..."

print_info "Building frontend..."
npm run build

print_info "Deploying to Vercel production..."
vercel --prod

echo ""
echo "=================================================="
echo "✨ Frontend Update Complete!"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo "   1. Verify frontend is working:"
echo "      open https://metroa-demo.vercel.app"
echo ""
echo "   2. Test backend connection:"
echo "      curl $PUBLIC_URL/health"
echo ""
echo "   3. Check Vercel deployment:"
echo "      open https://vercel.com/interact-hq/metroa-demo"
echo ""
echo "=================================================="

