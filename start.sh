#!/bin/bash

# Mini AI Analyst Startup Script
# This script helps you start the application with different configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Mini AI Analyst Startup${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_status "Docker is running"
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating a template..."
        cat > .env << EOF
# Required for AI Analysis
GEMINI_LLM_API_KEY=your_gemini_api_key_here

# Supabase Configuration (Required)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Database Configuration (Optional - defaults to local PostgreSQL)
DATABASE_URL=postgresql://user:password@postgres:5432/ai_analyst
POSTGRES_DB=ai_analyst
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Redis Configuration (Optional - for background tasks)
REDIS_URL=redis://redis:6379/0

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production

# S3 Storage (Optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1
EOF
        print_warning "Please edit the .env file with your actual configuration values before starting the application."
        exit 1
    fi
    print_status ".env file found"
}

# Function to start development mode
start_development() {
    print_status "Starting development mode..."
    docker-compose up --build backend frontend postgres redis celery
}

# Function to start production mode
start_production() {
    print_status "Starting production mode..."
    docker-compose --profile production up --build -d
}

# Function to start with monitoring
start_with_monitoring() {
    print_status "Starting with monitoring services..."
    docker-compose up --build -d
    print_status "Services started. Access points:"
    echo -e "  ${BLUE}Frontend:${NC} http://localhost:3000"
    echo -e "  ${BLUE}Backend API:${NC} http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC} http://localhost:8000/docs"
    echo -e "  ${BLUE}Flower Monitoring:${NC} http://localhost:5555"
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_status "Services stopped"
}

# Function to view logs
view_logs() {
    print_status "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f
}

# Function to check service status
check_status() {
    print_status "Checking service status..."
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_warning "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_status "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev          Start development mode (backend, frontend, postgres, redis, celery)"
    echo "  prod         Start production mode (includes nginx)"
    echo "  monitor      Start with monitoring services (includes flower)"
    echo "  stop         Stop all services"
    echo "  logs         View logs from all services"
    echo "  status       Check service status"
    echo "  cleanup      Remove all containers, networks, and volumes"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev       # Start development mode"
    echo "  $0 prod      # Start production mode"
    echo "  $0 monitor   # Start with monitoring"
}

# Main script logic
main() {
    print_header
    
    # Check prerequisites
    check_docker
    check_env_file
    
    # Parse command line arguments
    case "${1:-help}" in
        "dev")
            start_development
            ;;
        "prod")
            start_production
            ;;
        "monitor")
            start_with_monitoring
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            view_logs
            ;;
        "status")
            check_status
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@" 