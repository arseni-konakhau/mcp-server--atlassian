#!/bin/bash

# MCP Atlassian Test Environment Setup Script
# This script sets up everything needed for testing the MCP Atlassian server

set -e  # Exit on any error

# Detect Python command first (python3 takes precedence)
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found. Please install Python 3.8+"
    exit 1
fi

# Create and activate virtual environment
echo "🐍 Creating Python virtual environment..."
if ! $PYTHON_CMD -m venv .venv --without-pip 2>/dev/null; then
    echo "⚠️ Standard venv failed, retrying with system packages..."
    if ! $PYTHON_CMD -m venv .venv --system-site-packages 2>/dev/null; then
        echo "❌ Critical: Failed to create virtual environment"
        echo "Possible solutions:"
        echo "1. Ensure Python development headers are installed (python3-dev or python3-devel package)"
        echo "2. Check Python installation with: $PYTHON_CMD --version"
        echo "3. Try reinstalling Python with:"
        echo "   - Linux: sudo apt install python3-venv"
        echo "   - Mac: brew reinstall python"
        exit 1
    fi
fi

# Verify the virtual environment was created properly
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ Virtual environment creation incomplete - missing Python binary"
    exit 1
fi

source .venv/bin/activate || { echo "❌ Failed to activate virtual environment"; exit 1; }
# Ensure UV targets the active environment
export UV_ACTIVE=1

# Verify basic Python functionality
if ! python -c "import sys; print(sys.version)" >/dev/null 2>&1; then
    echo "❌ Python environment is corrupted - cannot import standard libraries"
    echo "Try reinstalling Python or using a different version"
    exit 1
fi

# Install pip if missing
if ! command -v pip &> /dev/null; then
    echo "📦 Bootstrapping pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $PYTHON_CMD get-pip.py || { echo "❌ Failed to install pip"; exit 1; }
    rm get-pip.py
fi

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

function install_with_pip() {
    echo ""
    echo "Installing minimal dependencies with pip..."
    REQUIRED_PACKAGES=(
        "python-dotenv"
        "click"
        "requests"
        "pydantic"
        "atlassian-python-api"
    )
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        echo "Installing $package..."
        if $PYTHON_CMD -m pip install "$package"; then
            echo "✓ $package installed successfully"
        else
            echo "✗ Failed to install $package"
            echo "You may need to install it manually"
        fi
    done
    
    # Special handling for local mcp package
    echo "Installing mcp (local package)..."
    if $PYTHON_CMD -m pip install -e .; then
        echo "✓ mcp installed successfully"
    else
        echo "✗ Failed to install mcp"
        echo "Note: mcp is a local package - make sure you're in the project root"
    fi
}

# Check if UV is available
echo ""
echo "🔧 Checking UV package manager..."
if command -v uv &> /dev/null; then
    echo "✅ UV is available: $(uv --version)"
    echo "Installing dependencies with UV..."
    if uv sync; then
        echo "✅ Dependencies installed successfully with UV!"
    else
        echo "⚠️  UV installation failed, falling back to pip..."
        install_with_pip
    fi
else
    echo "✗ UV is not available"
    install_with_pip
fi

# Step 2: Verify environment configuration
echo ""
echo "⚙️  Verifying environment configuration..."
REQUIRED_VARS=(
    "JIRA_URL"
    "JIRA_USERNAME" 
    "JIRA_API_TOKEN"
    "CONFLUENCE_URL"
    "CONFLUENCE_USERNAME"
    "CONFLUENCE_API_TOKEN"
)

if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    exit 1
fi

# Verify all required variables are set
MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^$var=" .env; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    printf ' - %s\n' "${MISSING_VARS[@]}"
    echo "Please edit .env file with these credentials"
    exit 1
else
    echo "✅ All required environment variables are present"
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
echo "📖 For detailed guidance, see: RUN_PROJECT_GUIDE.md"
