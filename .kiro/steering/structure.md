# Project Structure

## Directory Organization

The Personal Automation Bot follows a modular architecture with clear separation of concerns. Each component is designed to be independently testable and maintainable.

```
personal_automation_bot/
├── bot/                  # Telegram bot interface
│   ├── __init__.py
│   ├── commands/         # Command handlers
│   ├── conversations/    # Multi-step conversation handlers
│   └── keyboards/        # Inline keyboard definitions
│
├── config/               # Configuration management
│   ├── __init__.py
│   ├── settings.py       # Global settings
│   └── credentials.py    # Credential management
│
├── services/             # Core service modules
│   ├── __init__.py
│   ├── calendar/         # Google Calendar integration
│   │   ├── __init__.py
│   │   ├── client.py     # Calendar API client
│   │   └── models.py     # Event data models
│   │
│   ├── content/          # AI content generation
│   │   ├── __init__.py
│   │   ├── text.py       # Text generation
│   │   └── image.py      # Image generation
│   │
│   ├── documents/        # Storage integration
│   │   ├── __init__.py
│   │   ├── drive.py      # Google Drive integration
│   │   └── notion.py     # Notion integration
│   │
│   ├── email/            # Gmail integration
│   │   ├── __init__.py
│   │   ├── client.py     # Gmail API client
│   │   └── models.py     # Email data models
│   │
│   ├── flows/            # Workflow automation
│   │   ├── __init__.py
│   │   ├── engine.py     # Workflow execution engine
│   │   └── triggers.py   # Workflow triggers
│   │
│   ├── rag/              # Retrieval-augmented generation
│   │   ├── __init__.py
│   │   ├── indexer.py    # Document indexing
│   │   └── retriever.py  # Context retrieval
│   │
│   └── social/           # Social media publishing
│       ├── __init__.py
│       ├── buffer.py     # Buffer integration
│       └── metricool.py  # Metricool integration
│
├── tests/                # Test suite
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures
│   ├── test_bot.py
│   └── test_services/    # Service-specific tests
│
└── utils/                # Shared utilities
    ├── __init__.py
    ├── auth.py           # Authentication helpers
    ├── logging.py        # Logging configuration
    └── storage.py        # Local storage utilities
```

## Architecture Patterns

### Service Layer Pattern

Each functional area is implemented as a service with a clear API:

- **Service Interface**: Defines the public API for the service
- **Service Implementation**: Contains the business logic
- **Models**: Data structures used by the service

### Dependency Injection

Services are designed to accept dependencies through constructors:

```python
class EmailService:
    def __init__(self, gmail_client, config, storage):
        self.gmail_client = gmail_client
        self.config = config
        self.storage = storage
```

### Repository Pattern

Data access is abstracted through repositories:

```python
class DocumentRepository:
    def save(self, document):
        pass

    def find_by_id(self, document_id):
        pass

    def search(self, query):
        pass
```

## Coding Conventions

### File Organization

- Each module should have a clear single responsibility
- Related functionality should be grouped in the same package
- Implementation details should be hidden behind clear interfaces

### Import Style

- Standard library imports first
- Third-party imports second
- Local application imports last
- Use absolute imports for clarity

```python
# Standard library
import os
import json
from datetime import datetime

# Third-party
import telegram
from google.oauth2 import credentials

# Local application
from personal_automation_bot.config import settings
from personal_automation_bot.services.email import EmailService
```

### Error Handling

- Use custom exception classes for domain-specific errors
- Handle exceptions at appropriate levels
- Log exceptions with context information
- Provide user-friendly error messages

## Data Flow

1. User sends command to Telegram bot
2. Bot handler processes command and calls appropriate service
3. Service performs business logic, possibly calling other services
4. Results are returned to bot handler
5. Bot formats and sends response to user

## Extension Points

The system is designed to be extended in the following ways:

1. **New Services**: Add new modules in the services directory
2. **Alternative Implementations**: Replace service implementations while maintaining interfaces
3. **New Commands**: Add new command handlers in the bot/commands directory
4. **New Workflows**: Define new workflows as JSON configurations
