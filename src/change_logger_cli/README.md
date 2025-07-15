# Changelog Generator

## 🚀 Quick Install

### One-line install (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/megh-khaire/change-logger/main/install.sh | bash
```

### Install from GitHub

```bash
pip install git+https://github.com/megh-khaire/change-logger.git
```

### Install from source

```bash
git clone https://github.com/megh-khaire/change-logger.git
cd change-logger
pip install -e .
```

## ⚡ Quick Start

1. **Set up your OpenAI API key:**

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **Generate a changelog:**

   ```bash
   change-logger generate --auto
   ```

That's it! 🎉

## 📖 Usage

### Basic Commands

```bash
# Generate changelog automatically from last version tag
change-logger generate --auto

# Generate changelog from specific range
change-logger generate --from v1.0.0 --to HEAD

# Save to file
change-logger generate --auto --output CHANGELOG.md

# Show repository information
change-logger info

# List version tags
change-logger tags

# Show commits between references
change-logger commits v1.0.0 HEAD
```

### Advanced Usage

```bash
# Custom template
change-logger generate --auto --template "# My Custom Changelog\n{content}"

# Different repository
change-logger generate --auto --repo /path/to/repo

# Specific commit range
change-logger generate --from abc123 --to def456
```

## 🛠️ Requirements

- **Python 3.10+**
- **Git repository**
- **OpenAI API key** (for AI-powered features)
