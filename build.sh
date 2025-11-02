#!/bin/bash

echo "🏗️  Building Transport System..."

# Build Frontend
echo "📦 Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# Install Backend Dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo "✅ Build complete!"
