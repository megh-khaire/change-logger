#!/bin/bash

# Installation script for changelog generator

set -e

echo "🚀 Installing Changelog Generator..."

# Check if Python 3.10+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.10+ from https://python.org"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    echo "   Please install pip or use: python3 -m ensurepip"
    exit 1
fi

# Use pip3 if available, otherwise fall back to pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10 or higher is required. Current version: $python_version"
    exit 1
fi

# Install the package
echo "📦 Installing changelog generator..."

# Check if we're in the source directory or installing remotely
if [ -f "pyproject.toml" ] && [ -d "src" ]; then
    echo "📁 Installing from local source..."
    $PIP_CMD install -e .
else
    echo "🌐 Installing from GitHub..."
    $PIP_CMD install git+https://github.com/megh-khaire/change-logger.git
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set."
    echo "   Please set it with: export OPENAI_API_KEY='your-api-key-here'"
    echo "   Or create a .env file in your project root."
    echo ""
fi

# Test installation
echo "🧪 Testing installation..."
if change-logger --help &> /dev/null; then
    echo "✅ Installation successful!"
    echo ""
    echo "Available commands:"
    echo "  change-logger  (or changelog-gen)"
    echo ""
    echo "Usage examples:"
    echo "  change-logger generate --auto"
    echo "  change-logger generate --from v1.0.0 --to HEAD"
    echo "  change-logger tags"
    echo "  change-logger info"
    echo ""
    echo "For more help: change-logger --help"
else
    echo "❌ Installation failed. Please check for errors above."
    exit 1
fi

echo ""
echo "🎉 Installation complete! Ready to generate changelogs!"
echo ""
echo "📖 Quick Start:"
echo "   1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'"
echo "   2. Generate a changelog: change-logger generate --auto"
echo ""
echo "📚 More help: change-logger --help"
