# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Tasks

### Setting up the environment
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your GitLab URL and API token
```

### Running tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_api_client.py
```

### Linting and type checking
```bash
# Run linting
flake8 src/ scripts/ --max-line-length=100

# Run type checking
mypy src/ scripts/ --ignore-missing-imports

# Auto-format code
black src/ scripts/ --line-length=100
```

### Running the main scripts

#### Branch Rename (Enhanced)
```bash
# Dry run mode (preview changes)
python scripts/rename_branches.py --dry-run

# Rename branches for specific groups
python scripts/rename_branches.py --groups "AI-ML-Services" "Research Repos"

# Custom branch names
python scripts/rename_branches.py --old-branch develop --new-branch main

# Debug mode with detailed logging
python scripts/rename_branches.py --log-level DEBUG
```

#### Issue Creation (Enhanced)
```bash
# Interactive mode (default)
python scripts/create_issues.py

# List available templates
python scripts/create_issues.py --list-templates

# Create from template
python scripts/create_issues.py ProjectName --template feature \
  --vars "feature_name=User Authentication" \
  --vars "description=Implement OAuth2" \
  --vars "acceptance_criteria=Users can login with Google"

# Import from CSV
python scripts/create_issues.py ProjectName --import examples/issues_import.csv

# Import with template (for ML experiments)
python scripts/create_issues.py ProjectName --import examples/ml_experiments.csv \
  --template ml-experiment

# Create single issue from command line
python scripts/create_issues.py ProjectName \
  --title "Fix memory leak" \
  --description "Memory usage increases over time" \
  --labels bug critical \
  --due-date 2024-01-30 \
  --weight 8

# Dry run for any operation
python scripts/create_issues.py ProjectName --import issues.csv --dry-run
```

#### Legacy Issue Creation
```bash
# Still available for backward compatibility
python 03_create_gitlab_issues.py "ProjectName" "issues/legacy-format.txt"
```

## High-Level Architecture

### Module Structure
The codebase follows a modular architecture to promote reusability and maintainability:

- **src/api/**: GitLab API client with automatic pagination, rate limiting, and retry logic
  - `client.py`: Main GitLabClient class that wraps all API operations
  - `exceptions.py`: Custom exception hierarchy for better error handling

- **src/models/**: Data models with validation
  - `issue.py`: Issue, IssueCreate, IssueTemplate models
  - `project.py`: Project models
  - `branch.py`: Branch and operation tracking models

- **src/services/**: Business logic layer
  - `issue_service.py`: Issue creation with templates, bulk import, validation
  - `branch_service.py`: Branch operations (to be implemented)

- **src/utils/**: Shared utilities
  - `config.py`: Configuration management that merges YAML config with env variables
  - `logger.py`: Advanced logging with color support and operation tracking
  - `progress.py`: Progress bars and spinners for long operations
  - `validators.py`: Input validation for issues, projects, and files

- **scripts/**: CLI entry points
  - `rename_branches.py`: Enhanced branch renaming with progress tracking
  - `create_issues.py`: Full-featured issue creation with templates

- **templates/issues/**: Issue templates
  - `epic.yaml`: Epic template for large features
  - `research.yaml`: Research task template
  - `ml-experiment.yaml`: ML experiment tracking template

### Key Design Patterns

1. **Configuration Cascade**: Environment variables override config.yaml values
2. **Graceful Degradation**: Progress bars fall back to simple counters if dependencies missing
3. **Rate Limiting**: Built into API client to respect GitLab limits
4. **Dry Run Mode**: All destructive operations support preview mode
5. **Comprehensive Logging**: Structured logging with operation context

### API Client Features
- Automatic pagination for all list operations
- Exponential backoff retry for transient failures
- Rate limiting with configurable requests per second
- Session reuse with connection pooling
- Type hints throughout for better IDE support

### Error Handling Strategy
- Custom exception hierarchy for different error types
- Graceful fallbacks for missing dependencies
- Detailed error logging with context
- Operation rollback support (planned)

## Important Implementation Notes

1. **Always use the modular API client** instead of direct requests
2. **Check dry_run mode** before any destructive operations
3. **Use ProgressTracker** for any operation processing multiple items
4. **Log operations** using OperationLogger context manager
5. **Validate configuration** before starting operations

## Future Enhancements Planned
- Concurrent processing with thread pools
- Operation checkpointing for resume capability
- Redis caching for frequently accessed data
- Web UI dashboard for monitoring
- Webhook integration for real-time updates
- Comprehensive test suite with mocking