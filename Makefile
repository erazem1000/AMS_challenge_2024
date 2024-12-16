# Define Docker services
UNIGRADICON_SERVICE = unigradicon
VALIDACIJA_SERVICE = validacija

# Default action
all: help

# Build and start services
up:
	docker-compose up -d

# Run individual services using docker-compose
run-unigradicon:
	docker-compose run --rm $(UNIGRADICON_SERVICE)

run-validacija:
	docker-compose run --rm $(VALIDACIJA_SERVICE)

# Stop services and remove containers/volumes
down:
	docker-compose down --volumes --remove-orphans

# Helper menu
help:
	@echo "Makefile for Docker Containers"
	@echo "Usage: make <target>"
	@echo "Available targets:"
	@echo "  up                 - Start all services"
	@echo "  run-unigradicon    - Run the Unigradicon service"
	@echo "  run-validacija     - Run the Validacija service"
	@echo "  down               - Stop and clean up"