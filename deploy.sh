#!/bin/bash

# Mini Dungeon Master Discord Bot Deployment Script
# This script helps set up and deploy the bot

set -e

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to check if virtual environment exists
check_venv() {
    if [ -d "venv" ]; then
        print_status "Virtual environment found"
        return 0
    else
        print_warning "Virtual environment not found"
        return 1
    fi
}

# Function to create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
}

# Function to activate virtual environment
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment activation failed"
        exit 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Function to check environment file
check_env() {
    if [ -f ".env" ]; then
        print_success "Environment file found"
        return 0
    else
        print_warning "Environment file not found"
        return 1
    fi
}

# Function to create environment file
create_env() {
    print_status "Creating environment file..."
    cat > .env << EOF
# Required: Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# Optional: Bot Configuration
COMMAND_PREFIX=!
BOT_STATUS=!help | Mini Dungeon Master
LOG_LEVEL=INFO
LOG_FILE=logs/discord_bot.log

# Optional: Database Configuration
DATABASE_PATH=data/dungeon_master.db

# Optional: LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-3.5-turbo
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Performance Configuration
CACHE_ENABLED=true
CACHE_TTL_SECONDS=300
CACHE_MAX_SIZE=1000
MAX_MESSAGE_LENGTH=2000
CLEANUP_INTERVAL_HOURS=1

# Optional: Rate Limiting
COOLDOWN_EXPLORE=30
COOLDOWN_ATTACK=5
COOLDOWN_USE=10
COOLDOWN_START=60
TIMEOUT_CHOICE=300
TIMEOUT_COMBAT=60
TIMEOUT_ITEM_SELECTION=60

# Optional: Game Configuration
GAME_MAX_HEALTH=100
GAME_STARTING_HEALTH=100
GAME_STARTING_LEVEL=1
GAME_EXP_PER_LEVEL=100
GAME_MAX_INVENTORY=20
GAME_MIN_DAMAGE=10
GAME_MAX_DAMAGE=25
GAME_HEALING_POTION=30
GAME_SESSION_TIMEOUT=30
EOF
    print_success "Environment file created"
    print_warning "Please edit .env file and set your Discord bot token!"
}

# Function to create directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs data
    print_success "Directories created"
}

# Function to check if bot token is set
check_token() {
    if [ -f ".env" ]; then
        if grep -q "DISCORD_TOKEN=your_discord_bot_token_here" .env; then
            print_error "Please set your Discord bot token in .env file"
            return 1
        else
            print_success "Discord bot token configured"
            return 0
        fi
    else
        print_error "Environment file not found"
        return 1
    fi
}

# Function to run the bot
run_bot() {
    print_status "Starting the bot..."
    python main.py
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    if command_exists pytest; then
        pytest tests/ -v
    else
        print_warning "pytest not found, skipping tests"
    fi
}

# Function to show help
show_help() {
    echo "Mini Dungeon Master Discord Bot Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup     - Set up the bot environment (default)"
    echo "  install   - Install dependencies"
    echo "  run       - Run the bot"
    echo "  test      - Run tests"
    echo "  docker    - Deploy using Docker"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Set up the bot environment"
    echo "  $0 run      # Run the bot"
    echo "  $0 docker   # Deploy using Docker"
}

# Function to deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."
    
    if ! command_exists docker; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning "Creating .env file for Docker deployment..."
        create_env
        print_error "Please edit .env file and set your Discord bot token before running Docker!"
        exit 1
    fi
    
    # Check if token is set
    if ! check_token; then
        exit 1
    fi
    
    print_status "Building and starting Docker containers..."
    docker-compose up -d --build
    
    print_success "Bot deployed with Docker!"
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
}

# Main script logic
main() {
    COMMAND=${1:-setup}
    
    case $COMMAND in
        setup)
            print_status "Setting up Mini Dungeon Master Discord Bot..."
            
            # Check Python
            if ! check_python; then
                exit 1
            fi
            
            # Create virtual environment if needed
            if ! check_venv; then
                create_venv
            fi
            
            # Activate virtual environment
            activate_venv
            
            # Install dependencies
            install_dependencies
            
            # Create environment file if needed
            if ! check_env; then
                create_env
            fi
            
            # Create directories
            create_directories
            
            print_success "Setup complete!"
            print_warning "Please edit .env file and set your Discord bot token before running the bot."
            ;;
            
        install)
            print_status "Installing dependencies..."
            
            if ! check_python; then
                exit 1
            fi
            
            if ! check_venv; then
                create_venv
            fi
            
            activate_venv
            install_dependencies
            
            print_success "Dependencies installed!"
            ;;
            
        run)
            print_status "Running the bot..."
            
            if ! check_python; then
                exit 1
            fi
            
            if ! check_venv; then
                print_error "Virtual environment not found. Run 'setup' first."
                exit 1
            fi
            
            activate_venv
            
            if ! check_token; then
                exit 1
            fi
            
            run_bot
            ;;
            
        test)
            print_status "Running tests..."
            
            if ! check_python; then
                exit 1
            fi
            
            if ! check_venv; then
                print_error "Virtual environment not found. Run 'setup' first."
                exit 1
            fi
            
            activate_venv
            run_tests
            ;;
            
        docker)
            deploy_docker
            ;;
            
        help|--help|-h)
            show_help
            ;;
            
        *)
            print_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"