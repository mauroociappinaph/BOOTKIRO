# Technical Stack

## Core Technologies

- **Language**: Python 3.8+
- **Bot Framework**: python-telegram-bot
- **Authentication**: OAuth 2.0 for Google services
- **Vector Database**: FAISS or Chroma for local vector storage
- **LLM Integration**: OpenAI API (free tier) or local models via llama-index

## Key Dependencies

- `python-telegram-bot`: Telegram bot API wrapper
- `google-api-python-client`: Google API client libraries
- `openai`: OpenAI API client for text and image generation
- `langchain`: Framework for LLM applications
- `llama-index`: Framework for RAG implementations
- `faiss-cpu`: Vector database for efficient similarity search
- `chromadb`: Vector database alternative
- `notion-client`: Notion API client
- `pytest`: Testing framework
- `python-dotenv`: Environment variable management

## Project Structure

The project follows a modular architecture with separate service components:

```
personal_automation_bot/
├── bot/            # Telegram bot interface
├── config/         # Configuration management
├── services/       # Core service modules
│   ├── calendar/   # Google Calendar integration
│   ├── content/    # AI content generation
│   ├── documents/  # Storage integration (Drive/Notion)
│   ├── email/      # Gmail integration
│   ├── flows/      # Workflow automation
│   ├── rag/        # Retrieval-augmented generation
│   └── social/     # Social media publishing
├── tests/          # Test suite
└── utils/          # Shared utilities
```

## Common Commands

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Running

```bash
# Start the bot
python main.py

# Run in development mode with auto-reload
python main.py --dev
```

### Testing

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_telegram_bot.py

# Run with coverage
pytest --cov=personal_automation_bot
```

### Deployment

```bash
# Local deployment as service
sudo cp deployment/personal_automation_bot.service /etc/systemd/system/
sudo systemctl enable personal_automation_bot
sudo systemctl start personal_automation_bot

# Check status
sudo systemctl status personal_automation_bot
```

## Development Guidelines

- Use environment variables for all secrets and configuration
- Follow PEP 8 style guidelines
- Write unit tests for all new functionality
- Document public APIs using docstrings
- Use async/await for I/O-bound operations
- Implement proper error handling and logging
