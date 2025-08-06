#!/bin/bash

# MCP Atlassian Test Environment Setup Script
# This script sets up everything needed for testing the MCP Atlassian server

set -e  # Exit on any error

echo "🚀 Setting up MCP Atlassian test environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root directory."
    exit 1
fi

# Step 1: Install dependencies
echo ""
echo "📦 Installing dependencies..."
# Detect and validate Python command (python3 takes precedence)
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found. Please install Python 3.8+"
    exit 1
fi

# Verify Python version is 3+
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$PYTHON_VERSION" < "3" ]]; then
    echo "❌ Error: Python 3+ required (found $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Using Python $PYTHON_VERSION"

$PYTHON_CMD _install_dependencies.py

# Step 2: Setup environment file
echo ""
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.debug" ]; then
        cp .env.debug .env
        echo "✅ Created .env from .env.debug template"
        echo "📝 Please edit .env file with your actual Atlassian credentials:"
        echo "   - JIRA_URL=https://your-company.atlassian.net"
        echo "   - JIRA_USERNAME=your.email@company.com"
        echo "   - JIRA_API_TOKEN=your_api_token"
        echo "   - CONFLUENCE_URL=https://your-company.atlassian.net/wiki"
        echo "   - CONFLUENCE_USERNAME=your.email@company.com"
        echo "   - CONFLUENCE_API_TOKEN=your_api_token"
    else
        echo "❌ Error: .env.debug template not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Step 3: Check if UV is available
echo ""
echo "🔧 Checking UV package manager..."
if command -v uv &> /dev/null; then
    echo "✅ UV is available: $(uv --version)"
else
    echo "📥 Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    echo "✅ UV installed successfully"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Atlassian credentials"
echo "2. Run the test: uv run $PYTHON_CMD simple_test.py --verbose"
echo ""
echo "🔗 Quick commands:"
echo "   Test connection: uv run $PYTHON_CMD simple_test.py --verbose"
echo "   Run MCP server: uv run mcp-atlassian --env-file .env --read-only --verbose"
echo ""
echo "📖 For detailed guidance, see: TESTING_GUIDE.md"
