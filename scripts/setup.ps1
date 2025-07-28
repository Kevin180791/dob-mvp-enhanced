# DOB-MVP Setup Script for Windows
# This script sets up the DOB-MVP environment and starts the services

Write-Host "=== DOB-MVP Setup Script ===" -ForegroundColor Green
Write-Host "This script will set up the DOB-MVP environment and start the services."

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Host "Error: Docker is not installed. Please install Docker and try again." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "Error: Docker Compose is not installed. Please install Docker Compose and try again." -ForegroundColor Red
    exit 1
}

# Check if .env file exists, if not create from example
if (-not (Test-Path .env)) {
    Write-Host "No .env file found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit the .env file and add your API keys." -ForegroundColor Yellow
    Write-Host "Press Enter to continue or Ctrl+C to abort..." -ForegroundColor Yellow
    Read-Host
}

# Create uploads directory if it doesn't exist
if (-not (Test-Path backend/uploads)) {
    New-Item -ItemType Directory -Path backend/uploads | Out-Null
    Write-Host "Created uploads directory." -ForegroundColor Green
}

# Build and start the services
Write-Host "Building and starting services..." -ForegroundColor Green
docker-compose up -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Green
Start-Sleep -Seconds 10

# Check if services are running
Write-Host "Checking services..." -ForegroundColor Green
$services = docker-compose ps

if ($services -match "backend.*Up") {
    Write-Host "Backend is running." -ForegroundColor Green
} else {
    Write-Host "Backend is not running. Please check the logs with 'docker-compose logs backend'." -ForegroundColor Red
}

if ($services -match "frontend.*Up") {
    Write-Host "Frontend is running." -ForegroundColor Green
} else {
    Write-Host "Frontend is not running. Please check the logs with 'docker-compose logs frontend'." -ForegroundColor Red
}

if ($services -match "postgres.*Up") {
    Write-Host "PostgreSQL is running." -ForegroundColor Green
} else {
    Write-Host "PostgreSQL is not running. Please check the logs with 'docker-compose logs postgres'." -ForegroundColor Red
}

if ($services -match "qdrant.*Up") {
    Write-Host "Qdrant is running." -ForegroundColor Green
} else {
    Write-Host "Qdrant is not running. Please check the logs with 'docker-compose logs qdrant'." -ForegroundColor Red
}

if ($services -match "neo4j.*Up") {
    Write-Host "Neo4j is running." -ForegroundColor Green
} else {
    Write-Host "Neo4j is not running. Please check the logs with 'docker-compose logs neo4j'." -ForegroundColor Red
}

if ($services -match "ollama.*Up") {
    Write-Host "Ollama is running." -ForegroundColor Green
} else {
    Write-Host "Ollama is not running. If you're using an external Ollama instance, make sure it's configured in .env." -ForegroundColor Yellow
}

# Print access URLs
Write-Host "`n=== DOB-MVP Access URLs ===" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "Backend API: http://localhost:3001" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:3001/docs" -ForegroundColor Green
Write-Host "Neo4j Browser: http://localhost:7474" -ForegroundColor Green

Write-Host "`nSetup complete!" -ForegroundColor Green

