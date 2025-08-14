#!/bin/bash

# MCP Atlassian Server - Fixed Startup Script
# This script handles Python environment setup more robustly

set -e  # Exit on any error

echo "🚀 Starting MCP Atlassian Server Setup..."
echo "================================================"

# Step 1: Check Python installation
echo ""
echo "1️⃣ Checking Python installation..."

# Find Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found in PATH"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
echo "✅ Found Python: $PYTHON_VERSION"

# Step 2: Check if UV is installed
echo ""
echo "2️⃣ Checking UV package manager..."

if ! command -v uv &> /dev/null; then
    echo "📥 Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "❌ Failed to install UV. Please install it manually:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi

echo "✅ UV is available: $(uv --version)"

# Step 3: Check environment file
echo ""
echo "3️⃣ Checking environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "⚠️  No .env file found. Creating from env.example..."
        cp env.example .env
        echo "📝 Please edit .env file with your Atlassian credentials"
    else
        echo "❌ Error: No .env file found and no env.example to copy from"
        exit 1
    fi
else
    echo "✅ .env file exists"
fi

# Step 4: Install dependencies with UV
echo ""
echo "4️⃣ Installing dependencies with UV..."

# Clean up any existing virtual environment
if [ -d ".venv" ]; then
    echo "🧹 Removing existing virtual environment..."
    rm -rf .venv
fi

# Create new virtual environment with UV
echo "📦 Creating virtual environment and installing dependencies..."
if uv venv; then
    echo "✅ Virtual environment created"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Install dependencies
if uv sync; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    echo "Trying alternative installation method..."
    
    # Try pip install as fallback
    if uv pip install -e .; then
        echo "✅ Dependencies installed via pip"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Step 5: Verify installation
echo ""
echo "5️⃣ Verifying installation..."

# Test if we can import the package
if uv run python -c "import mcp_atlassian; print('✅ MCP Atlassian package imported successfully')" 2>/dev/null; then
    echo "✅ Installation verified"
else
    echo "⚠️  Warning: Could not verify package import"
    echo "This might be normal if the package hasn't been built yet"
fi

# Step 6: Display next steps
echo ""
echo "================================================"
echo "✨ Setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Edit .env file with your Atlassian credentials:"
echo "   - JIRA_URL"
echo "   - JIRA_USERNAME"
echo "   - JIRA_API_TOKEN"
echo "   - CONFLUENCE_URL"
echo "   - CONFLUENCE_USERNAME"
echo "   - CONFLUENCE_API_TOKEN"
echo ""
echo "2. Test the server:"
echo "   uv run mcp-atlassian --env-file .env --verbose"
echo ""
echo "3. Or run with specific environment file:"
echo "   uv run mcp-atlassian --env-file env.akonakhau --verbose"
echo ""
echo "================================================"
