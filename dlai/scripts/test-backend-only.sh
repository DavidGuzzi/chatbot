#!/bin/bash
# Test only the backend quickly without Docker

echo "🚀 Testing Backend Only (No Docker)"

# Check if virtual environment exists
if [ ! -d "new_cb" ]; then
    echo "❌ Virtual environment 'new_cb' not found."
    echo "   Please create it first: python -m venv new_cb"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source new_cb/bin/activate

# Install/update backend requirements
echo "📦 Installing backend requirements..."
pip install -r backend/requirements.txt

# Check if .env exists and has OpenAI key
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi

if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY might not be configured in .env"
fi

# Check if data files exist
if [ ! -f "tiendas_detalle.csv" ] || [ ! -f "maestro_tiendas.csv" ]; then
    echo "❌ CSV data files not found. Please ensure:"
    echo "   - tiendas_detalle.csv"
    echo "   - maestro_tiendas.csv"
    exit 1
fi

echo "✅ All checks passed. Starting backend..."
echo "🔗 Backend will be available at: http://localhost:5000"
echo "🔗 Health check: http://localhost:5000/api/health"
echo ""
echo "Press Ctrl+C to stop"

# Start the backend
python backend/app.py