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

#### File-Based Issue Creation (SIMPLIFIED!)
```bash
# Add markdown/text files to the issues/ folder, then sync:
python scripts/sync_issues.py PROJECT_ID

# Preview what will be created
python scripts/sync_issues.py PROJECT_ID --dry-run

# Use API instead of curl
python scripts/sync_issues.py PROJECT_ID --use-api

# Generate shell script
python scripts/sync_issues.py PROJECT_ID --generate-script

# Example: Create issue file
cat > issues/new-feature.md << EOF
---
title: Add User Dashboard
labels: [feature, frontend]
weight: 5
---

Create a dashboard showing user statistics and recent activity.

#ui #react
EOF

# Then sync to GitLab
python scripts/sync_issues.py 123
```

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

#### Weekly Productivity Reports (NEW!)
```bash
# Generate weekly report for specific groups and save as HTML
python scripts/weekly_reports.py --groups 1,2,3 --output weekly_report.html

# Send email report to team
python scripts/weekly_reports.py --groups 1,2,3 --email team@company.com,manager@company.com

# Generate report for specific team members
python scripts/weekly_reports.py --groups 1,2,3 --team john.doe,jane.smith --output report.json

# Generate 2-week report with email delivery
python scripts/weekly_reports.py --groups 1,2,3 --weeks 2 --email team@company.com \
  --team-name "AI Development Team"

# Test email configuration
python scripts/weekly_reports.py --test-email your.email@company.com

# Generate report with attachments
python scripts/weekly_reports.py --groups 1,2,3 --email team@company.com \
  --email-attachments "analytics.xlsx,metrics.pdf"

# Dry run mode (generate but don't send email)
python scripts/weekly_reports.py --groups 1,2,3 --email team@company.com --dry-run
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
  - `weekly_reports.py`: Weekly productivity reporting with team metrics
  - `email_service.py`: Email delivery system for reports
  - `analytics_advanced.py`: Advanced analytics with health scoring

- **src/utils/**: Shared utilities
  - `config.py`: Configuration management that merges YAML config with env variables
  - `logger.py`: Advanced logging with color support and operation tracking
  - `progress.py`: Progress bars and spinners for long operations
  - `validators.py`: Input validation for issues, projects, and files

- **scripts/**: CLI entry points
  - `rename_branches.py`: Enhanced branch renaming with progress tracking
  - `create_issues.py`: Full-featured issue creation with templates
  - `weekly_reports.py`: Generate and send weekly productivity reports
  - `export_analytics.py`: Export analytics to Excel and other formats

- **templates/**: Template files
  - **issues/**: Issue templates
    - `epic.yaml`: Epic template for large features
    - `research.yaml`: Research task template
    - `ml-experiment.yaml`: ML experiment tracking template
  - `weekly_report_email.py`: HTML email template generator for reports

### Key Design Patterns

1. **Configuration Cascade**: Environment variables override config.yaml values
2. **Graceful Degradation**: Progress bars fall back to simple counters if dependencies missing
3. **Rate Limiting**: Built into API client to respect GitLab limits
4. **Dry Run Mode**: All destructive operations support preview mode
5. **Comprehensive Logging**: Structured logging with operation context
6. **Email-First Reporting**: Weekly reports optimized for email delivery with embedded charts
7. **Health Scoring**: Automated project health assessment with actionable recommendations

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

## Weekly Productivity Reports Features

### Core Capabilities
- **Team Activity Metrics**: Commits, merge requests, issues across all repositories
- **Project Health Scoring**: Automated health assessment with A-F grades
- **Individual Contributor Analytics**: Productivity and collaboration scoring
- **Executive Summary**: Key metrics and highlights for leadership
- **Actionable Insights**: Automated recommendations for team improvement

### Email Delivery
- **Professional HTML Templates**: Clean, mobile-responsive email reports
- **Embedded Charts**: Visual analytics embedded directly in emails
- **Multi-format Support**: HTML, JSON, and Markdown output options
- **Attachment Support**: Include additional files with email reports
- **Email Testing**: Built-in test functionality to verify configuration

### Configuration Options
- **Team Focus**: Filter metrics to specific team members
- **Time Periods**: Generate reports for 1-4 weeks of data
- **Group Selection**: Analyze specific GitLab groups or entire organization
- **SMTP Configuration**: Support for various email providers (Gmail, Outlook, etc.)

### Setup for Weekly Reports

#### Email Configuration
Add to your `.env` file:
```bash
# SMTP Configuration for email reports
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=gitlab-analytics@company.com
SMTP_FROM_NAME=GitLab Analytics
```

#### Example config.yaml Email Section
```yaml
email:
  smtp_server: smtp.company.com
  smtp_port: 587
  use_tls: true
  from_name: "Development Team Analytics"
```

## Future Enhancements Planned
- Concurrent processing with thread pools
- Operation checkpointing for resume capability
- Redis caching for frequently accessed data
- Web UI dashboard for monitoring
- Webhook integration for real-time updates
- Slack/Teams integration for weekly reports
- Custom report templates and branding