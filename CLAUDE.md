# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Primary Interface

The main entry point is the interactive menu system:
```bash
python glt_menu.py
```

This provides 9 numbered options for GitLab operations (branch renaming, dashboards, reports, issue creation, analytics). Each option calls a corresponding script in `scripts/` directory via subprocess.

Alternative CLI interface available via `glt.py` which provides natural language command parsing and REPL functionality.

## Essential Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with GITLAB_URL and GITLAB_TOKEN
```

### Testing
```bash
# Run all tests with coverage (80% minimum)
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m api          # API tests only

# Run single test file
pytest tests/unit/api/test_client.py
```

### Linting and Code Quality
```bash
# Run linting
flake8 src/ scripts/ --max-line-length=100

# Type checking
mypy src/ scripts/ --ignore-missing-imports

# Auto-format code
black src/ scripts/ --line-length=100
```

## Architecture Overview

### Modular Design
- **src/api/**: GitLab API client with automatic pagination, rate limiting, retry logic
- **src/models/**: Pydantic data models for issues, projects, branches
- **src/services/**: Business logic layer (issue creation, analytics, email delivery)
- **src/utils/**: Shared utilities (config, logging, progress bars, caching)
- **src/templates/**: HTML email templates for reports
- **scripts/**: CLI entry points that orchestrate services

### Key Design Patterns
1. **Configuration Cascade**: Environment variables override config.yaml values
2. **Dry Run Mode**: All destructive operations support `--dry-run` preview
3. **Progress Tracking**: Long operations show real-time progress
4. **Rate Limiting**: Built into API client to respect GitLab limits
5. **Graceful Degradation**: Features degrade gracefully if dependencies missing

### API Client (`src/api/client.py`)
Central `GitLabClient` class provides:
- Automatic pagination for all list operations
- Exponential backoff retry for transient failures
- Rate limiting with configurable requests per second
- Session reuse with connection pooling
- Comprehensive error handling

### Services Layer
- **WeeklyProductivityReporter**: Advanced analytics with contributor deduplication
- **IssueService**: Template-based issue creation with bulk import
- **EmailService**: SMTP delivery for HTML reports
- **Analytics**: Project health scoring and trend analysis

## Implementation Guidelines

### When Adding New Features
1. **Use the modular API client** instead of direct requests
2. **Always implement dry-run mode** for destructive operations
3. **Add progress tracking** for operations processing multiple items
4. **Use OperationLogger** context manager for structured logging
5. **Validate configuration** before starting operations
6. **Include comprehensive tests** with pytest markers

### Error Handling
- Custom exception hierarchy in `src/api/exceptions.py`
- Graceful fallbacks for missing dependencies
- Detailed error logging with operation context
- User-friendly error messages in CLI

### Configuration Management
Config loading order (highest priority first):
1. Command line arguments
2. Environment variables (.env file)
3. Configuration files (config.yaml)

Required environment variables:
- `GITLAB_URL`: GitLab instance URL
- `GITLAB_TOKEN`: API token with appropriate scopes

### Testing Strategy
- Unit tests for all services and utilities
- Integration tests for complete workflows
- API tests marked with `@pytest.mark.api`
- 80% coverage minimum enforced by pytest

### CLI Interface Patterns
Both interfaces (`glt_menu.py` and `glt.py`) follow the pattern:
1. Parse arguments/get user input
2. Validate configuration
3. Initialize services with progress tracking
4. Execute operations with dry-run support
5. Generate reports and provide feedback

## Important Notes

- **Contributor Deduplication**: Weekly reports map multiple identities to single contributors using config mapping
- **Client-Side Filtering**: API responses are filtered client-side for accurate date ranges
- **Branch Analytics**: Three-method analysis (git diff, ownership tracking, dual metrics)
- **Email Templates**: Use shadcn/ui-inspired design for professional appearance
- **Health Scoring**: Automated project assessment with A-F grades and recommendations