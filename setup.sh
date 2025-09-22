#!/bin/bash

echo "🚀 Setting up Event Sponsor Agent"

# Create necessary directories
mkdir -p secrets
mkdir -p config

# Rename magic to subagents if it exists
if [ -d "chat_with_human/magic" ]; then
    echo "📁 Renaming 'magic' folder to 'subagents'..."
    mv chat_with_human/magic chat_with_human/subagents
fi

# Move tokens to secrets folder if they exist in root
if [ -f "token.json" ]; then
    echo "📁 Moving token.json to secrets folder..."
    mv token.json secrets/
fi

if [ -f "client_secret.json" ]; then
    echo "📁 Moving client_secret.json to secrets folder..."
    mv client_secret.json secrets/
fi

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Created .env file. Please edit it with your API keys."
    fi
fi

# Rename frontend server file
if [ -f "frontend/combined_server.py" ]; then
    mv frontend/combined_server.py frontend/server.py
    echo "📁 Renamed combined_server.py to server.py"
fi

echo "✅ Setup complete!"