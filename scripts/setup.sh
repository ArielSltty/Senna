#!/bin/bash

# 🛠️ Senna Wallet Setup Script
# One-time setup for development environment

set -e  # Exit on any error

echo "🧠 Senna Wallet - Initial Setup"
echo "=========================================="

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

# Check if running on Windows
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    print_error "Windows detected. Please use WSL2 for development."
    exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_NODE="18.0.0"
if [ "$(printf '%s\n' "$REQUIRED_NODE" "$NODE_VERSION" | sort -V | head -n1)" = "$REQUIRED_NODE" ]; then
    print_success "Node.js version $NODE_VERSION (>= $REQUIRED_NODE)"
else
    print_error "Node.js version $NODE_VERSION is too old. Please upgrade to 18+"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
REQUIRED_PYTHON="3.8.0"
if [ "$(printf '%s\n' "$REQUIRED_PYTHON" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_PYTHON" ]; then
    print_success "Python version $PYTHON_VERSION (>= $REQUIRED_PYTHON)"
else
    print_error "Python version $PYTHON_VERSION is too old. Please upgrade to 3.8+"
    exit 1
fi

# Check git
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git"
    exit 1
fi
print_success "Git installed"

print_status "Setting up project structure..."

# Create necessary directories
mkdir -p logs
mkdir -p frontend/assets
mkdir -p frontend/assets/icons
mkdir -p frontend/assets/images
mkdir -p contracts/deployments
mkdir -p backend/__pycache__

print_success "Project directories created"

# Backend setup
print_status "Setting up Python backend..."

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found in backend directory"
    exit 1
fi

# Create environment files
print_status "Setting up environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Created .env from example. Please update with your actual values."
    else
        print_error ".env.example not found"
        exit 1
    fi
else
    print_success ".env already exists"
fi

# Create contracts environment file
if [ ! -f ".contracts.env" ]; then
    print_status "Creating contracts environment file..."
    cat > .contracts.env << EOF
# Senna Wallet Contract Addresses
# Update these after contract deployment

SOMI_TOKEN_ADDRESS=0x0000000000000000000000000000000000000000
SENNA_WALLET_ADDRESS=0x0000000000000000000000000000000000000000

# Network Configuration
SOMNIA_RPC_URL=https://dream-rpc.somnia.network/
SOMNIA_CHAIN_ID=50312
SOMNIA_EXPLORER_URL=https://shannon-explorer.somnia.network/
EOF
    print_success "Contracts environment file created"
fi

cd ..

# Frontend setup
print_status "Setting up frontend..."

cd frontend

# Check if package.json exists
if [ ! -f "package.json" ]; then
    print_warning "No frontend package.json found. Using root package.json..."
    cd ..
else
    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    npm install
    print_success "Frontend dependencies installed"
    cd ..
fi

# Contracts setup
print_status "Setting up smart contracts..."

cd contracts

# Check if package.json exists
if [ ! -f "package.json" ]; then
    print_warning "No contracts package.json found. Using root package.json..."
    cd ..
else
    # Install contract dependencies
    print_status "Installing contract dependencies..."
    npm install
    print_success "Contract dependencies installed"
    
    # Create contracts environment
    if [ ! -f ".env" ]; then
        print_status "Creating contracts environment file..."
        cat > .env << EOF
# Contracts Deployment Environment
PRIVATE_KEY=your_private_key_here
SOMNIA_RPC_URL=https://dream-rpc.somnia.network/
ETHERSCAN_API_KEY=your_etherscan_api_key_here

# Optional
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here
REPORT_GAS=true
EOF
        print_warning "Created contracts .env. Please update with your actual values."
    fi
    cd ..
fi

# Root dependencies
print_status "Installing root dependencies..."
if [ -f "package.json" ]; then
    npm install
    print_success "Root dependencies installed"
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x scripts/*.sh
chmod +x scripts/dev.sh
chmod +x scripts/deploy.sh
print_success "Scripts made executable"

# Generate documentation
print_status "Generating initial documentation..."
if command -v npm &> /dev/null && [ -f "package.json" ]; then
    npm run docs || print_warning "Documentation generation skipped"
fi

print_success "Documentation generated"

# Final setup
print_status "Running initial build..."

# Try to build contracts
cd contracts
if [ -f "package.json" ] && npm run compile &> /dev/null; then
    print_success "Smart contracts compiled"
else
    print_warning "Smart contract compilation skipped"
fi
cd ..

print_status "Setup completed successfully!"
echo ""
echo "🎉 Senna Wallet is ready for development!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your DeepSeek API key and other settings"
echo "2. Update contracts/.env with your private key for deployment"
echo "3. Run './scripts/dev.sh' to start the development servers"
echo "4. Visit http://localhost:3000 to see the application"
echo ""
echo "Important files to configure:"
echo "  - backend/.env (API keys, blockchain settings)"
echo "  - contracts/.env (deployment keys)"
echo "  - frontend/.env (frontend configuration)"
echo ""

print_warning "Don't forget to add your actual API keys and private keys to the .env files!"