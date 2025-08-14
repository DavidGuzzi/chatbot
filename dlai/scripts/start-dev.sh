#!/bin/bash
# Development startup script

echo "🚀 Starting Gatorade AB Testing Dashboard in Development Mode"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY might not be configured in .env"
    echo "   Make sure to set your OpenAI API key for the chatbot to work."
fi

echo "🐳 Building and starting containers..."

# Start development environment
docker-compose -f docker-compose.dev.yml up --build

echo "🎉 Development environment started!"
echo "📝 Access the application at:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:5000"
echo "   Health Check: http://localhost:5000/api/health"