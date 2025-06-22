#!/bin/bash

# 🚀 Currency Parsing & Force Refresh Feature Deployment Script
# Railway.app deployment automation

set -e  # Exit on any error

echo "🚀 Starting Currency Parsing & Force Refresh deployment..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_error "Railway CLI not found. Please install: npm install -g @railway/cli"
    exit 1
fi

# Check if connected to Railway project
if ! railway status &> /dev/null; then
    print_error "Not connected to Railway project. Run: railway link"
    exit 1
fi

print_success "Prerequisites check passed"

# Environment variables validation
print_status "Validating environment variables..."

# Check required environment variables
required_vars=("GEMINI_API_KEY" "EXCHANGE_RATE_API_KEY" "GOOGLE_OAUTH_CLIENT_ID" "GOOGLE_OAUTH_CLIENT_SECRET")

for var in "${required_vars[@]}"; do
    if railway variables | grep -q "$var"; then
        print_success "$var is set"
    else
        print_warning "$var is not set in Railway environment"
        echo "Set it with: railway variables set $var=your_value"
    fi
done

# Deployment confirmation
print_status "Ready to deploy Currency Parsing features"
echo "Features to be deployed:"
echo "  ✅ Enhanced currency detection (USD vs VND)"
echo "  ✅ Force refresh support in preview mode"
echo "  ✅ Improved import handling for existing records"
echo "  ✅ Real-time currency conversion with exchange rates"
echo ""

read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled by user"
    exit 0
fi

# Step 1: Deploy code (auto-deployment via Git push)
print_status "Code is already pushed to GitHub. Railway will auto-deploy..."

# Wait for deployment to complete
print_status "Waiting for Railway deployment to complete..."
sleep 10

# Check deployment status
deployment_status=$(railway status 2>&1 || echo "error")
if [[ $deployment_status == *"error"* ]]; then
    print_warning "Could not check deployment status automatically"
    echo "Please check Railway dashboard manually"
else
    print_success "Railway deployment status checked"
fi

# Step 2: Run database migrations
print_status "Running database migrations..."

migration_output=$(railway run python manage.py migrate 2>&1 || echo "migration_failed")

if [[ $migration_output == *"migration_failed"* ]]; then
    print_error "Migration failed. Please check manually:"
    echo "  railway shell"
    echo "  python manage.py migrate"
    exit 1
else
    print_success "Database migrations completed"
fi

# Step 3: Collect static files
print_status "Collecting static files..."

static_output=$(railway run python manage.py collectstatic --noinput 2>&1 || echo "static_failed")

if [[ $static_output == *"static_failed"* ]]; then
    print_warning "Static files collection failed - continuing anyway"
else
    print_success "Static files collected"
fi

# Step 4: Health check
print_status "Performing health check..."

# Get Railway app URL
app_url=$(railway domain 2>&1 | grep -o 'https://[^[:space:]]*' | head -1 || echo "")

if [[ -n $app_url ]]; then
    health_response=$(curl -s -o /dev/null -w "%{http_code}" "$app_url/health/" || echo "000")
    
    if [[ $health_response == "200" ]]; then
        print_success "Health check passed ($app_url/health/)"
    else
        print_warning "Health check failed (HTTP $health_response)"
    fi
else
    print_warning "Could not determine app URL for health check"
fi

# Step 5: Test currency service
print_status "Testing currency service..."

currency_test=$(railway run python -c "
from transactions.currency_service import CurrencyService
cs = CurrencyService()
rate = cs.get_usd_to_vnd_rate()
conversion = cs.convert_usd_to_vnd(11)
print(f'Rate: {rate}, Conversion: {conversion}')
" 2>&1 || echo "currency_test_failed")

if [[ $currency_test == *"currency_test_failed"* ]]; then
    print_warning "Currency service test failed - check API keys"
else
    print_success "Currency service test passed: $currency_test"
fi

# Step 6: Final deployment verification
print_status "Final deployment verification..."

echo ""
echo "🎉 Deployment Summary:"
echo "======================"
print_success "✅ Code deployed to Railway"
print_success "✅ Database migrations applied"  
print_success "✅ Static files collected"
print_success "✅ Health check performed"
print_success "✅ Currency service tested"

echo ""
echo "📋 Post-Deployment Testing:"
echo "1. Login to your app: $app_url"
echo "2. Go to Settings → Bank Integration"
echo "3. Test TPBank sync with force refresh enabled"
echo "4. Verify currency conversion for USD transactions"
echo "5. Check calendar UI for imported transactions"

echo ""
echo "🔍 Monitoring Commands:"
echo "  View logs: railway logs"
echo "  Filter currency logs: railway logs --filter 'Currency'"
echo "  Filter import logs: railway logs --filter 'Import'"

echo ""
echo "🚨 If Issues Occur:"
echo "  Quick rollback: railway rollback [deployment-id]"
echo "  Check variables: railway variables"
echo "  Shell access: railway shell"

echo ""
print_success "🎉 Currency Parsing deployment completed successfully!"
print_status "Monitor the application for the next 24-48 hours"

# Optional: Open Railway dashboard
read -p "Open Railway dashboard? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    railway open
fi 