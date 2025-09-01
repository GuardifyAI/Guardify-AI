#!/bin/bash

# Build script for Guardify-AI Docker deployment
# This script provides options for single container and 4-container (Redis + Backend + Celery + Frontend) builds

set -e  # Exit on error

echo "🚀 Guardify-AI Docker Build Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_warning "Docker Compose not found. Multi-container deployment will not be available."
        COMPOSE_AVAILABLE=false
    else
        COMPOSE_AVAILABLE=true
    fi
    
    print_success "Prerequisites check passed"
}

# Create necessary directories
setup_directories() {
    print_info "Setting up directories..."
    mkdir -p logs data credentials
    print_success "Directories created"
}

# Check environment file
check_environment() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your actual values before proceeding"
            read -p "Press Enter to continue after editing .env file..."
        else
            print_error ".env.example not found. Cannot create .env file."
            exit 1
        fi
    else
        print_success "Environment file found"
    fi
}

# Build single container
build_single_container() {
    print_info "Building single container image..."
    
    docker build -t guardify-ai:latest . || {
        print_error "Failed to build single container image"
        exit 1
    }
    
    print_success "Single container image built successfully"
}

# Build multi-container setup
build_multi_container() {
    if [ "$COMPOSE_AVAILABLE" = false ]; then
        print_error "Docker Compose not available. Cannot build multi-container setup."
        return 1
    fi
    
    print_info "Building multi-container setup..."
    
    # Try docker compose first (newer syntax), then docker-compose
    if docker compose build 2>/dev/null; then
        print_success "Multi-container images built successfully (using 'docker compose')"
    elif docker-compose build; then
        print_success "Multi-container images built successfully (using 'docker-compose')"
    else
        print_error "Failed to build multi-container images"
        exit 1
    fi
}

# Run single container
run_single_container() {
    print_info "Running single container..."
    
    # Stop existing container if running
    docker stop guardify-ai 2>/dev/null || true
    docker rm guardify-ai 2>/dev/null || true
    
    docker run -d \
        --name guardify-ai \
        -p 80:80 \
        -p 8574:8574 \
        -p 5555:5555 \
        -v "$(pwd)/credentials:/app/credentials" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        --env-file .env \
        guardify-ai:latest || {
        print_error "Failed to run single container"
        exit 1
    }
    
    print_success "Single container is running"
    print_info "Frontend: http://localhost"
    print_info "Backend API: http://localhost:8574/app/"
    print_info "Flower monitoring: http://localhost:5555"
}

# Run multi-container setup
run_multi_container() {
    if [ "$COMPOSE_AVAILABLE" = false ]; then
        print_error "Docker Compose not available. Cannot run multi-container setup."
        return 1
    fi
    
    print_info "Running 4-container setup..."
    print_warning "Make sure you have configured external PostgreSQL service!"
    
    # Try docker compose first (newer syntax), then docker-compose
    if docker compose up -d 2>/dev/null; then
        print_success "4-container setup is running (using 'docker compose')"
    elif docker-compose up -d; then
        print_success "4-container setup is running (using 'docker-compose')"
    else
        print_error "Failed to run 4-container setup"
        exit 1
    fi
    
    print_info "Containers created: redis, backend, celery, frontend"
    print_info "Frontend: http://localhost"
    print_info "Backend API: http://localhost:8574/app/"
    print_info "Note: Only external PostgreSQL required"
}

# Show logs
show_logs() {
    case $1 in
        "single")
            docker logs -f guardify-ai
            ;;
        "multi")
            if docker compose version &> /dev/null; then
                docker compose logs -f
            else
                docker-compose logs -f
            fi
            ;;
        *)
            print_error "Invalid logs option. Use 'single' or 'multi'"
            exit 1
            ;;
    esac
}

# Stop containers
stop_containers() {
    case $1 in
        "single")
            docker stop guardify-ai 2>/dev/null || true
            docker rm guardify-ai 2>/dev/null || true
            print_success "Single container stopped"
            ;;
        "multi")
            if docker compose version &> /dev/null; then
                docker compose down
            else
                docker-compose down
            fi
            print_success "Multi-container setup stopped"
            ;;
        "all")
            docker stop guardify-ai 2>/dev/null || true
            docker rm guardify-ai 2>/dev/null || true
            if docker compose version &> /dev/null; then
                docker compose down 2>/dev/null || true
            else
                docker-compose down 2>/dev/null || true
            fi
            print_success "All containers stopped"
            ;;
        *)
            print_error "Invalid stop option. Use 'single', 'multi', or 'all'"
            exit 1
            ;;
    esac
}

# Show help
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build single    Build single container image"
    echo "  build multi     Build multi-container setup"
    echo "  build all       Build both setups"
    echo "  run single      Run single container"
    echo "  run multi       Run multi-container setup"
    echo "  logs single     Show single container logs"
    echo "  logs multi      Show multi-container logs"
    echo "  stop single     Stop single container"
    echo "  stop multi      Stop multi-container setup"
    echo "  stop all        Stop all containers"
    echo "  status          Show container status"
    echo "  clean           Remove all images and containers"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build single"
    echo "  $0 run multi"
    echo "  $0 logs multi"
    echo "  $0 stop all"
}

# Show status
show_status() {
    print_info "Container Status:"
    echo ""
    
    # Single container status
    if docker ps -q -f name=guardify-ai | grep -q .; then
        echo "Single Container: 🟢 Running"
    else
        echo "Single Container: 🔴 Stopped"
    fi
    
    # Multi-container status
    if docker compose ps -q 2>/dev/null | grep -q . || docker-compose ps -q 2>/dev/null | grep -q .; then
        echo "Multi-Container: 🟢 Running"
    else
        echo "Multi-Container: 🔴 Stopped"
    fi
    
    echo ""
    print_info "Active Containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Clean up
clean_up() {
    print_warning "This will remove all Guardify-AI containers and images. Are you sure? (y/N)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_info "Clean up cancelled"
        return
    fi
    
    print_info "Cleaning up containers and images..."
    
    # Stop and remove containers
    docker stop guardify-ai 2>/dev/null || true
    docker rm guardify-ai 2>/dev/null || true
    
    if docker compose version &> /dev/null; then
        docker compose down --rmi all --volumes 2>/dev/null || true
    else
        docker-compose down --rmi all --volumes 2>/dev/null || true
    fi
    
    # Remove images
    docker rmi guardify-ai:latest 2>/dev/null || true
    docker rmi $(docker images -q -f "dangling=true") 2>/dev/null || true
    
    print_success "Clean up completed"
}

# Main script logic
main() {
    check_prerequisites
    setup_directories
    
    case "${1:-help}" in
        "build")
            check_environment
            case "${2:-help}" in
                "single")
                    build_single_container
                    ;;
                "multi")
                    build_multi_container
                    ;;
                "all")
                    build_single_container
                    build_multi_container
                    ;;
                *)
                    print_error "Invalid build option. Use 'single', 'multi', or 'all'"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
        "run")
            check_environment
            case "${2:-help}" in
                "single")
                    run_single_container
                    ;;
                "multi")
                    run_multi_container
                    ;;
                *)
                    print_error "Invalid run option. Use 'single' or 'multi'"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
        "logs")
            show_logs "${2:-multi}"
            ;;
        "stop")
            stop_containers "${2:-all}"
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_up
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"