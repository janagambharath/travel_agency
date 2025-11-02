#!/bin/bash
set -e

echo "🏗️  Building Transport System..."

# Install Node.js (Render specific)
echo "📦 Installing Node.js..."
if ! command -v node &> /dev/null; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm install 18
fi

# Build Frontend
echo "📦 Building React frontend..."
cd frontend
npm ci
npm run build
cd ..

# Install Backend Dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete!"
