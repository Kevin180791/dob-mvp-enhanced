#!/bin/bash

# DOB-MVP Enhanced Development Environment Setup Script
echo "🚀 Setting up DOB-MVP Enhanced development environment..."

# Update package lists
sudo apt-get update

# Install system dependencies
sudo apt-get install -y \
    build-essential \
        curl \
            git \
                unzip \
                    wget \
                        software-properties-common \
                            apt-transport-https \
                                ca-certificates \
                                    gnupg \
                                        lsb-release

                                        # Extract project files from ZIP if it exists
                                        if [ -f "dob-mvp-enhanced-code.zip" ]; then
                                            echo "📦 Extracting project files..."
                                                unzip -q dob-mvp-enhanced-code.zip
                                                    # Move files from extracted directory to workspace root
                                                        if [ -d "dob-mvp-enhanced" ]; then
                                                                cp -r dob-mvp-enhanced/* .
                                                                        rm -rf dob-mvp-enhanced
                                                                                rm dob-mvp-enhanced-code.zip
                                                                                    fi
                                                                                    fi

                                                                                    # Install Python dependencies for backend
                                                                                    if [ -f "backend/requirements.txt" ]; then
                                                                                        echo "🐍 Installing Python dependencies..."
                                                                                            pip install --upgrade pip
                                                                                                pip install -r backend/requirements.txt
                                                                                                fi

                                                                                                # Install Node.js dependencies for frontend
                                                                                                if [ -f "frontend/package.json" ]; then
                                                                                                    echo "📦 Installing Node.js dependencies..."
                                                                                                        cd frontend
                                                                                                            npm install
                                                                                                                cd ..
                                                                                                                fi
                                                                                                                
                                                                                                                # Create .env file from example if it doesn't exist
                                                                                                                if [ -f ".env.example" ] && [ ! -f ".env" ]; then
                                                                                                                    echo "⚙️ Creating .env file from template..."
                                                                                                                        cp .env.example .env
                                                                                                                            echo "Please update the .env file with your API keys and configuration."
                                                                                                                            fi
                                                                                                                            
                                                                                                                            # Set up pre-commit hooks (optional)
                                                                                                                            echo "🔧 Setting up development tools..."
                                                                                                                            pip install pre-commit black flake8 pylint
                                                                                                                            
                                                                                                                            # Make scripts executable
                                                                                                                            if [ -d "scripts" ]; then
                                                                                                                                chmod +x scripts/*.sh 2>/dev/null || true
                                                                                                                                fi
                                                                                                                                
                                                                                                                                echo "✅ Development environment setup complete!"
                                                                                                                                echo ""
                                                                                                                                echo "📋 Next steps:"
                                                                                                                                echo "1. Update .env file with your API keys"
                                                                                                                                echo "2. Start the backend: cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 3001"
                                                                                                                                echo "3. Start the frontend: cd frontend && npm run dev"
                                                                                                                                echo ""
                                                                                                                                echo "🌐 Access points:"
                                                                                                                                echo "- Backend API: http://localhost:3001"
                                                                                                                                echo "- Frontend: http://localhost:5173"
                                                                                                                                echo "- API Documentation: http://localhost:3001/docs"
