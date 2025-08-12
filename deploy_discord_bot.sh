#!/bin/bash

# Mini Dungeon Master Discord Bot Deployment Script
# This script automates the setup and deployment process

set -e  # Exit on any error

echo "🎮 Mini Dungeon Master Discord Bot - Deployment Script"
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

# Check if Python 3.8+ is installed
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python"
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        print_success "pip found"
        PIP_CMD="pip"
    else
        print_error "pip not found. Please install pip."
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Check environment variables
check_environment() {
    print_status "Checking environment variables..."
    
    if [ -z "$DISCORD_TOKEN" ]; then
        print_warning "DISCORD_TOKEN not set"
        echo "Please set your Discord bot token:"
        echo "export DISCORD_TOKEN='your_discord_bot_token_here'"
        echo ""
        read -p "Enter your Discord bot token: " DISCORD_TOKEN
        export DISCORD_TOKEN="$DISCORD_TOKEN"
    else
        print_success "DISCORD_TOKEN is set"
    fi
    
    # Check optional LLM settings
    if [ -z "$LLM_PROVIDER" ]; then
        print_status "LLM_PROVIDER not set, using default: ollama"
        export LLM_PROVIDER="ollama"
    fi
    
    if [ "$LLM_PROVIDER" = "ollama" ]; then
        if [ -z "$OLLAMA_BASE_URL" ]; then
            export OLLAMA_BASE_URL="http://localhost:11434"
        fi
        if [ -z "$OLLAMA_MODEL" ]; then
            export OLLAMA_MODEL="llama2"
        fi
        print_success "Ollama configuration: $OLLAMA_BASE_URL/$OLLAMA_MODEL"
    fi
}

# Run tests
run_tests() {
    print_status "Running bot tests..."
    
    if [ -f "test_discord_bot.py" ]; then
        $PYTHON_CMD test_discord_bot.py
        if [ $? -eq 0 ]; then
            print_success "All tests passed"
        else
            print_error "Tests failed"
            exit 1
        fi
    else
        print_warning "test_discord_bot.py not found, skipping tests"
    fi
}

# Create log directory
setup_logging() {
    print_status "Setting up logging..."
    
    mkdir -p logs
    touch logs/discord_bot.log
    print_success "Log directory created"
}

# Create systemd service file (if running as root)
create_service() {
    if [ "$EUID" -eq 0 ]; then
        print_status "Creating systemd service file..."
        
        cat > /etc/systemd/system/discord-bot.service << EOF
[Unit]
Description=Mini Dungeon Master Discord Bot
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$(pwd)
Environment=DISCORD_TOKEN=$DISCORD_TOKEN
Environment=LLM_PROVIDER=$LLM_PROVIDER
Environment=OLLAMA_BASE_URL=$OLLAMA_BASE_URL
Environment=OLLAMA_MODEL=$OLLAMA_MODEL
ExecStart=$PYTHON_CMD discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        print_success "Systemd service created"
        echo "To start the service: sudo systemctl start discord-bot"
        echo "To enable auto-start: sudo systemctl enable discord-bot"
    else
        print_warning "Not running as root, skipping systemd service creation"
    fi
}

# Main deployment function
main() {
    echo ""
    print_status "Starting deployment process..."
    
    check_python
    check_pip
    install_dependencies
    check_environment
    setup_logging
    run_tests
    create_service
    
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    echo "🎉 Your Discord bot is ready to run!"
    echo ""
    echo "To start the bot manually:"
    echo "  $PYTHON_CMD discord_bot.py"
    echo ""
    echo "To start with systemd (if service was created):"
    echo "  sudo systemctl start discord-bot"
    echo "  sudo systemctl enable discord-bot"
    echo ""
    echo "Bot commands:"
    echo "  !start - Begin your adventure"
    echo "  !help - Show help information"
    echo "  !debug - Show bot statistics (admin only)"
    echo ""
    echo "Logs will be written to: logs/discord_bot.log"
    echo ""
}

# Run main function
main "$@"