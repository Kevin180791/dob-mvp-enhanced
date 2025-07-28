#!/bin/bash

# DOB-MVP Setup Script
# This script sets up the DOB-MVP environment and starts the services

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== DOB-MVP Setup Script ===${NC}"
echo "This script will set up the DOB-MVP environment and start the services."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker and try again.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose and try again.${NC}"
    exit 1
fi

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit the .env file and add your API keys.${NC}"
    echo -e "${YELLOW}Press Enter to continue or Ctrl+C to abort...${NC}"
    read
fi

# Create uploads directory if it doesn't exist
mkdir -p backend/uploads
echo -e "${GREEN}Created uploads directory.${NC}"

# Build and start the services
echo -e "${GREEN}Building and starting services...${NC}"
docker-compose up -d

# Wait for services to start
echo -e "${GREEN}Waiting for services to start...${NC}"
sleep 10

# Check if services are running
echo -e "${GREEN}Checking services...${NC}"
if docker-compose ps | grep -q "backend.*Up"; then
    echo -e "${GREEN}Backend is running.${NC}"
else
    echo -e "${RED}Backend is not running. Please check the logs with 'docker-compose logs backend'.${NC}"
fi

if docker-compose ps | grep -q "frontend.*Up"; then
    echo -e "${GREEN}Frontend is running.${NC}"
else
    echo -e "${RED}Frontend is not running. Please check the logs with 'docker-compose logs frontend'.${NC}"
fi

if docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}PostgreSQL is running.${NC}"
else
    echo -e "${RED}PostgreSQL is not running. Please check the logs with 'docker-compose logs postgres'.${NC}"
fi

if docker-compose ps | grep -q "qdrant.*Up"; then
    echo -e "${GREEN}Qdrant is running.${NC}"
else
    echo -e "${RED}Qdrant is not running. Please check the logs with 'docker-compose logs qdrant'.${NC}"
fi

if docker-compose ps | grep -q "neo4j.*Up"; then
    echo -e "${GREEN}Neo4j is running.${NC}"
else
    echo -e "${RED}Neo4j is not running. Please check the logs with 'docker-compose logs neo4j'.${NC}"
fi

if docker-compose ps | grep -q "ollama.*Up"; then
    echo -e "${GREEN}Ollama is running.${NC}"
else
    echo -e "${YELLOW}Ollama is not running. If you're using an external Ollama instance, make sure it's configured in .env.${NC}"
fi

# Print access URLs
echo -e "\n${GREEN}=== DOB-MVP Access URLs ===${NC}"
echo -e "Frontend: ${GREEN}http://localhost:5173${NC}"
echo -e "Backend API: ${GREEN}http://localhost:3001${NC}"
echo -e "API Documentation: ${GREEN}http://localhost:3001/docs${NC}"
echo -e "Neo4j Browser: ${GREEN}http://localhost:7474${NC}"

echo -e "\n${GREEN}Setup complete!${NC}"

