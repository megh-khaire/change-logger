# Changelog Generation Agent 🤖

A sophisticated AI-powered agent that automatically generates professional changelogs from Git commit data. The agent analyzes commit messages and diffs to categorize changes and create comprehensive, well-formatted changelogs.

## ✨ Features

- **AI-Powered Analysis**: Uses OpenAI's GPT models to understand commit context and intent
- **Smart Categorization**: Automatically categorizes commits into features, bug fixes, documentation, etc.
- **Rich Descriptions**: Generates detailed descriptions of what each commit accomplishes
- **Professional Formatting**: Creates markdown-formatted changelogs ready for release notes
- **Flexible Configuration**: Customizable prompts and templates via YAML configuration
- **Comprehensive Testing**: 100% test coverage with unit and integration tests

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key

### Installation

1. **Install dependencies:**

   ```bash
   uv sync --extra test
   ```

2. **Set up your OpenAI API key:**

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

3. **Install the package in development mode:**

   ```bash
   uv pip install -e .
   ```

### Basic Usage

```python
from src.main import main
from src.models import Commit

# Create commit data
commits = [
    Commit(
        hash="abc123",
        message="Add user authentication system",
        diff="+class AuthService:\n+    def login(self, user):\n+        # Auth logic here"
    ),
    Commit(
        hash="def456",
        message="Fix memory leak in data processor",
        diff="-old_cache = {}\n+new_cache = WeakKeyDictionary()"
    )
]

# Generate changelog
changelog = generate_changelog_from_commits(commits)

print(changelog.title)
print(changelog.description)
print(changelog.summary)
```

## 🏗️ Architecture

The agent follows a clean, modular architecture:

```txt
src/
├── main.py          # Main pipeline orchestration
├── models.py        # Pydantic data models
├── llm.py          # OpenAI integration
├── prompt.py       # Prompt loading and formatting
└── template.py     # Output templates

resources/
└── prompts.yml     # AI prompt configurations

tests/
├── test_main.py           # Pipeline tests
├── test_models.py         # Data model tests
├── test_llm.py           # LLM integration tests
├── test_prompt.py        # Prompt handling tests
├── test_integration.py   # End-to-end tests
└── conftest.py          # Test configuration
```

## 📊 Pipeline Flow

1. **Input**: List of `Commit` objects (hash, message, diff)
2. **Enrichment**: Each commit is analyzed by AI to determine:
   - Category (feature, bug_fix, documentation, etc.)
   - Detailed description of changes
3. **Aggregation**: All enriched commits are formatted and combined
4. **Generation**: AI creates a final changelog with:
   - Professional title
   - Categorized description in markdown
   - Executive summary

## 🧪 Testing

The project includes comprehensive tests with 100% coverage:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_models.py -v          # Data model tests
pytest tests/test_integration.py -v     # Integration tests
```

## ⚙️ Configuration

### Prompts Configuration

Customize AI prompts in `resources/prompts.yml`:

```yaml
enrich_commit:
  system: |
    You are an expert software engineer that categorizes commits...
  user: |
    Commit message: {commit_message}
    Diff: {diff}

generate_changelog:
  system: |
    You are an expert that generates changelogs...
  user: |
    Commits: {commits}
```

### Categories

The agent automatically categorizes commits into:

- `feature` - New functionality
- `bug_fix` - Bug fixes and patches
- `refactor` - Code refactoring
- `documentation` - Documentation updates
- `test` - Test additions/improvements
- `chore` - Maintenance tasks
- `style` - Code formatting changes
- `security` - Security improvements
- `performance` - Performance optimizations
