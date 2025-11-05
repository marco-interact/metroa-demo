#!/bin/bash
################################################################################
# Deploy Frontend to Vercel with RunPod Backend Connection
# Run this on your LOCAL machine after backend is running on RunPod
# Date: 2025-11-05
################################################################################

set -e

echo "=================================================="
echo "🚀 Deploying Frontend to Vercel"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC}  $1"
}

print_error() {
    echo -e "${RED}❌${NC}  $1"
}

################################################################################
# Step 1: Check Backend URL
################################################################################

print_step "Step 1/5: Verifying backend connection..."

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_error ".env.production not found!"
    echo ""
    echo "Please create .env.production with your RunPod backend URL:"
    echo "   NEXT_PUBLIC_API_URL=\"https://YOUR_POD_ID-8000.proxy.runpod.net\""
    exit 1
fi

# Read backend URL from .env.production
BACKEND_URL=$(grep NEXT_PUBLIC_API_URL .env.production | cut -d '=' -f2 | tr -d '"')

if [ -z "$BACKEND_URL" ]; then
    print_error "NEXT_PUBLIC_API_URL not set in .env.production"
    exit 1
fi

print_info "Backend URL: $BACKEND_URL"

# Test backend connectivity
print_info "Testing backend connection..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    print_info "✅ Backend is responding (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "502" ]; then
    print_error "Backend returned 502 Bad Gateway"
    echo ""
    echo "This means the RunPod backend is not running."
    echo "Please run the following on your RunPod instance:"
    echo "   bash /workspace/colmap-demo/resume-runpod.sh"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_error "Backend is not responding (HTTP $HTTP_CODE)"
    echo ""
    echo "Please check:"
    echo "1. RunPod backend is running"
    echo "2. Backend URL in .env.production is correct"
    echo "3. RunPod pod is not paused or stopped"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

################################################################################
# Step 2: Install Dependencies
################################################################################

print_step "Step 2/5: Installing dependencies..."

npm install

print_info "✅ Dependencies installed"

################################################################################
# Step 3: Build Frontend
################################################################################

print_step "Step 3/5: Building frontend..."

# Set environment variable for build
export NEXT_PUBLIC_API_URL="$BACKEND_URL"

npm run build

print_info "✅ Frontend built successfully"

################################################################################
# Step 4: Test Build Locally (Optional)
################################################################################

print_step "Step 4/5: Testing build locally..."

print_info "Starting local server on http://localhost:3000"
print_info "Press Ctrl+C to stop and continue deployment"
echo ""

# Start local server in background
npm start &
LOCAL_PID=$!

# Wait a moment
sleep 3

# Test local server
if curl -s http://localhost:3000 > /dev/null; then
    print_info "✅ Local server running"
    echo ""
    echo "Visit: http://localhost:3000"
    echo "Press Ctrl+C when ready to deploy to Vercel"
    echo ""
    
    # Wait for user to interrupt
    wait $LOCAL_PID || true
else
    print_info "Local server test skipped"
    kill $LOCAL_PID 2>/dev/null || true
fi

################################################################################
# Step 5: Deploy to Vercel
################################################################################

print_step "Step 5/5: Deploying to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI not found!"
    echo ""
    echo "Install with: npm install -g vercel"
    exit 1
fi

print_info "Running Vercel deployment..."

# Deploy to production
vercel --prod --yes

print_info "✅ Deployment complete!"

################################################################################
# Deployment Complete
################################################################################

echo ""
echo "=================================================="
echo "✨ Frontend Deployment Complete!"
echo "=================================================="
echo ""
echo "📋 Configuration:"
echo "   • Backend URL: $BACKEND_URL"
echo "   • Backend Status: HTTP $HTTP_CODE"
echo ""
echo "📋 Next Steps:"
echo "1. Visit your Vercel deployment URL"
echo "2. Test the connection to backend"
echo "3. Check browser console for any errors"
echo ""
echo "📋 Troubleshooting:"
echo "   • If frontend can't connect to backend:"
echo "     - Verify backend is running: curl $BACKEND_URL/health"
echo "     - Check CORS settings in main.py"
echo "     - Check Vercel environment variables"
echo ""
echo "   • View backend logs on RunPod:"
echo "     tail -f /workspace/colmap-demo/backend.log"
echo ""
echo "=================================================="

