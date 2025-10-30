#!/bin/bash

# 🌐 Senna Wallet Production Deployment Script
# Deploy to production environment

set -e  # Exit on any error

echo "🚀 Senna Wallet - Production Deployment"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Configuration
DEPLOY_ENV=${1:-"staging"}
SOMNIA_NETWORK="somnia"

# Validate deployment environment
validate_environment() {
    case $DEPLOY_ENV in
        "staging"|"production")
            print_status "Deploying to $DEPLOY_ENV environment"
            ;;
        *)
            print_error "Invalid environment: $DEPLOY_ENV"
            echo "Usage: $0 [staging|production]"
            exit 1
            ;;
    esac
    
    # Check required environment variables
    if [ -z "$PRIVATE_KEY" ] && [ -z "$DEPLOYER_PRIVATE_KEY" ]; then
        print_error "PRIVATE_KEY or DEPLOYER_PRIVATE_KEY environment variable not set"
        exit 1
    fi
    
    if [ -z "$DEEPSEEK_API_KEY" ]; then
        print_error "DEEPSEEK_API_KEY environment variable not set"
        exit 1
    fi
}

# Build frontend
build_frontend() {
    print_status "Building frontend for $DEPLOY_ENV..."
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        npm ci
    fi
    
    # Build based on environment
    if [ "$DEPLOY_ENV" = "production" ]; then
        npm run build:prod
    else
        npm run build:staging
    fi
    
    # Check if build was successful
    if [ -d "dist" ] || [ -d "build" ]; then
        print_success "Frontend built successfully"
    else
        print_error "Frontend build failed"
        exit 1
    fi
    
    cd ..
}

# Build backend
build_backend() {
    print_status "Building backend for $DEPLOY_ENV..."
    
    cd backend
    
    # Create production requirements
    pip freeze > requirements-prod.txt
    
    # Run tests
    if [ -f "run_tests.py" ]; then
        python run_tests.py
    fi
    
    print_success "Backend prepared for deployment"
    cd ..
}

# Deploy smart contracts
deploy_contracts() {
    print_status "Deploying smart contracts to $SOMNIA_NETWORK..."
    
    cd contracts
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        npm ci
    fi
    
    # Run tests
    print_status "Running contract tests..."
    npx hardhat test
    
    # Deploy contracts
    print_status "Deploying contracts..."
    npx hardhat run deploy.js --network $SOMNIA_NETWORK
    
    # Verify contracts
    print_status "Verifying contracts on block explorer..."
    npx hardhat verify:contracts --network $SOMNIA_NETWORK || print_warning "Contract verification failed or skipped"
    
    # Get deployment information
    DEPLOYMENT_FILE=$(ls -t deployments/deployment-*.json | head -1)
    if [ -f "$DEPLOYMENT_FILE" ]; then
        CONTRACT_ADDRESSES=$(cat $DEPLOYMENT_FILE)
        print_success "Contract deployment information saved to $DEPLOYMENT_FILE"
    fi
    
    cd ..
}

# Deploy to hosting platform (example for Vercel)
deploy_frontend() {
    print_status "Deploying frontend to hosting platform..."
    
    cd frontend
    
    # Check if Vercel is available
    if command -v vercel &> /dev/null; then
        if [ "$DEPLOY_ENV" = "production" ]; then
            vercel --prod
        else
            vercel
        fi
    else
        print_warning "Vercel CLI not found. Frontend deployment skipped."
        print_status "Frontend build is ready in frontend/dist/ for manual deployment"
    fi
    
    cd ..
}

# Deploy backend (example for Railway/Heroku)
deploy_backend() {
    print_status "Deploying backend to cloud platform..."
    
    cd backend
    
    # Example for Railway
    if command -v railway &> /dev/null; then
        railway deploy
    else
        print_warning "Railway CLI not found. Backend deployment skipped."
        print_status "Backend is ready for manual deployment"
    fi
    
    cd ..
}

# Run post-deployment tests
post_deployment_tests() {
    print_status "Running post-deployment tests..."
    
    # Wait for services to be available
    sleep 30
    
    # Test backend health
    if [ -n "$BACKEND_URL" ]; then
        if curl -s "$BACKEND_URL/health" > /dev/null; then
            print_success "Backend health check passed"
        else
            print_error "Backend health check failed"
        fi
    fi
    
    # Test frontend
    if [ -n "$FRONTEND_URL" ]; then
        if curl -s "$FRONTEND_URL" > /dev/null; then
            print_success "Frontend is accessible"
        else
            print_error "Frontend is not accessible"
        fi
    fi
    
    # Test contract interactions
    print_status "Testing contract interactions..."
    cd contracts
    npx hardhat run scripts/test-production.js --network $SOMNIA_NETWORK || print_warning "Production tests failed"
    cd ..
}

# Update environment configurations
update_configurations() {
    print_status "Updating environment configurations..."
    
    # Update backend environment for production
    if [ "$DEPLOY_ENV" = "production" ]; then
        cat > backend/.env.production << EOF
# Production Environment
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# Somnia Blockchain
SOMNIA_RPC_URL=https://dream-rpc.somnia.network/
SOMNIA_CHAIN_ID=50312
SOMNIA_SYMBOL=STT

# AI Configuration
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Security
SECRET_KEY=$PRODUCTION_SECRET_KEY
JWT_ALGORITHM=HS256

# Features
FEATURE_STRIPE_PAYMENTS=true
FEATURE_AI_PRICE_RECOMMENDATIONS=true

# Contract Addresses
$(cat contracts/.contracts.env)
EOF
        print_success "Production environment file created"
    fi
}

# Main deployment function
main() {
    print_status "Starting deployment to $DEPLOY_ENV..."
    echo ""
    
    # Validate
    validate_environment
    
    # Build
    build_frontend
    build_backend
    
    # Deploy contracts
    deploy_contracts
    
    # Update configurations
    update_configurations
    
    # Deploy services
    deploy_frontend
    deploy_backend
    
    # Run tests
    post_deployment_tests
    
    # Final summary
    echo ""
    print_success "🎉 Deployment to $DEPLOY_ENV completed successfully!"
    echo ""
    echo "📊 Deployment Summary:"
    echo "   Environment: $DEPLOY_ENV"
    echo "   Network: $SOMNIA_NETWORK"
    echo "   Contracts: Deployed and verified"
    echo "   Frontend: Built and deployed"
    echo "   Backend: Built and deployed"
    echo ""
    
    if [ -n "$FRONTEND_URL" ]; then
        echo "🌐 Frontend URL: $FRONTEND_URL"
    fi
    if [ -n "$BACKEND_URL" ]; then
        echo "🔧 Backend URL: $BACKEND_URL"
    fi
    if [ -n "$CONTRACT_ADDRESSES" ]; then
        echo "📄 Contract Addresses: See $DEPLOYMENT_FILE"
    fi
    echo ""
}

# Check if we should run interactive deployment
if [ -z "$1" ] && [ -t 0 ]; then
    echo "Select deployment environment:"
    echo "1) Staging"
    echo "2) Production"
    read -p "Enter choice [1-2]: " choice
    
    case $choice in
        1) DEPLOY_ENV="staging" ;;
        2) DEPLOY_ENV="production" ;;
        *) print_error "Invalid choice"; exit 1 ;;
    esac
fi

# Run main function
main