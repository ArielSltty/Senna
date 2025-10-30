#!/bin/bash

# 🏃‍♂️ Senna Wallet Development Script
# Start all development services

set -e  # Exit on any error

echo "🧠 Senna Wallet - Development Environment"
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

# Check if setup has been run
check_setup() {
    if [ ! -d "backend/venv" ]; then
        print_error "Setup not completed. Please run './scripts/setup.sh' first."
        exit 1
    fi
    
    if [ ! -f "backend/.env" ]; then
        print_warning "backend/.env not found. Please run setup first."
    fi
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    print_success "All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM EXIT

# Start backend service
start_backend() {
    print_status "Starting backend server..."
    
    cd backend
    source venv/bin/activate
    
    # Check if required environment variables are set
    if [ -z "$DEEPSEEK_API_KEY" ] && [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    if [ -z "$DEEPSEEK_API_KEY" ] || [ "$DEEPSEEK_API_KEY" = "your_deepseek_api_key_here" ]; then
        print_warning "DeepSeek API key not set. AI features will not work."
        print_warning "Please set DEEPSEEK_API_KEY in backend/.env"
    fi
    
    # Start FastAPI server
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    sleep 3
    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_success "Backend server running on http://localhost:8000"
        print_success "API documentation: http://localhost:8000/docs"
    else
        print_error "Failed to start backend server"
        exit 1
    fi
}

# Start frontend service
start_frontend() {
    print_status "Starting frontend development server..."
    
    cd frontend
    
    # Check if we're using the root package.json or have a separate one
    if [ -f "package.json" ]; then
        # Start frontend dev server
        npm run dev &
    else
        # Use Python simple HTTP server as fallback
        print_status "Using Python HTTP server for frontend..."
        python3 -m http.server 3000 &
    fi
    
    FRONTEND_PID=$!
    cd ..
    
    sleep 3
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_success "Frontend server running on http://localhost:3000"
    else
        print_error "Failed to start frontend server"
        exit 1
    fi
}

# Start blockchain services (if needed)
start_blockchain() {
    print_status "Checking blockchain connection..."
    
    cd contracts
    
    # Check if Hardhat node is needed
    if [ -f "hardhat.config.js" ]; then
        print_status "Starting local blockchain node..."
        npx hardhat node &
        BLOCKCHAIN_PID=$!
        
        sleep 5
        if kill -0 $BLOCKCHAIN_PID 2>/dev/null; then
            print_success "Local blockchain node running on http://localhost:8545"
            
            # Deploy contracts to local node
            print_status "Deploying contracts to local network..."
            npx hardhat run deploy.js --network localhost
        else
            print_warning "Failed to start local blockchain node"
        fi
    else
        print_status "Using Somnia Testnet for blockchain operations"
    fi
    
    cd ..
}

# Health check services
health_check() {
    print_status "Performing health checks..."
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null; then
        print_success "Frontend health check passed"
    else
        print_warning "Frontend health check failed (might still be starting)"
    fi
    
    echo ""
    print_success "🎉 All services are starting up!"
    echo ""
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""
}

# Main execution
main() {
    check_setup
    
    print_status "Starting Senna Wallet development environment..."
    echo ""
    
    # Start services
    start_backend
    start_frontend
    start_blockchain
    
    # Wait a bit for services to start
    sleep 5
    
    # Health check
    health_check
    
    # Keep script running
    while true; do
        sleep 10
        
        # Check if services are still running
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            print_error "Backend server stopped unexpectedly"
            exit 1
        fi
        
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            print_error "Frontend server stopped unexpectedly"
            exit 1
        fi
    done
}

# Run main function
main