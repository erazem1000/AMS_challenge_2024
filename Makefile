# Define Docker services
REGISTRATION_SERVICE = registration
VALIDATION_SERVICE = validation

# Default action
all: help

# Build and start services
up:
	docker-compose up -d

# Run individual services using docker-compose
run-registration:
	docker-compose run --rm $(REGISTRATION_SERVICE)

run-validation:
	docker-compose run --rm $(VALIDATION_SERVICE)

# Stop services and remove containers/volumes
down:
	docker-compose down --volumes --remove-orphans

# Helper menu
help:
	@echo "Makefile for AMS Challenge uni/multi-GradICON docker Containers"
	@echo "Usage: make <target>"
	@echo "Available targets:"
	@echo "  up                 - Start all docker-compose services"
	@echo "  run-registration   - Run the registration servise"
	@echo "  run-validation     - Run the validation service"
	@echo "  down               - Stop and clean up"