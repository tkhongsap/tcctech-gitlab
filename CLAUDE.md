# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Interactive Menu Interface

### GitLab Tools CLI Menu
Use the interactive menu interface for easy access to all GitLab tools:

```bash
# Launch interactive menu
python glt_menu.py

# Options available:
# 1. 🔄 Rename Branches - Rename branches across multiple projects
# 2. 📊 Generate Executive Dashboard - Create HTML dashboards with analytics
# 3. 📅 Generate Weekly Report - Team productivity reports with email delivery
# 4. 📧 Send Report Email - Email HTML reports to teams
# 5. 🎯 Create Issues - Interactive or template-based issue creation
# 6. 📈 Analyze Projects - Deep project and group analytics
# 7. 💾 Export Analytics - Export data to Excel and other formats
# 8. 📋 Generate Code Changes Report - Track code activity across projects
# 9. 👋 Exit - Exit the program
```

### Menu Features
- **Group ID Display**: Shows group IDs and descriptions for easy selection
- **Default Email**: Pre-configured with totrakool.k@thaibev.com for weekly reports
- **Progress Tracking**: Real-time progress bars for long operations
- **Dry Run Mode**: Preview changes before execution

## Common Development Tasks

### Setting up the environment
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your GitLab URL and API token

# Required environment variables:
# GITLAB_URL=https://your-gitlab-instance.com
# GITLAB_API_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
# GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx  # Alternative name

# Optional email configuration for reports:
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@company.com
# SMTP_PASSWORD=your-app-password
```

### Running tests
```bash
# Run all tests (uses pytest.ini configuration)
pytest

# Run specific test file
pytest tests/unit/api/test_client.py

# Run by test markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m api          # API tests only

# Use the comprehensive test runner script
python run_tests.py

# Run specific test suite
python run_tests.py tests/unit/services/

# Skip slow tests
pytest -m "not slow"
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

#### GitLab Tools CLI (Unified Interface)
```bash
# Interactive mode
glt

# Natural language commands
glt rename branches in AI-ML-Services from trunk to main
glt create dashboard for AI team
glt analyze project 123
glt send weekly report to team@company.com

# Direct script commands
glt --script rename_branches --groups AI-ML-Services --dry-run
glt --script create_issues ProjectName --template feature
```

#### Interactive Menu Interface (Recommended)
```bash
# Launch numbered menu interface (easier than CLI arguments)
python glt_menu.py

# Select options by number (1-12)
# Includes group ID display and default settings
# Built-in dry-run modes for safety
```

#### File-Based Issue Creation
```bash
# Add markdown/text files to the issues/ folder, then sync:
python scripts/sync_issues.py PROJECT_ID

# Preview what will be created
python scripts/sync_issues.py PROJECT_ID --dry-run

# Use API instead of curl
python scripts/sync_issues.py PROJECT_ID --use-api

# Generate shell script
python scripts/sync_issues.py PROJECT_ID --generate-script

# Simplified script for specific project
python sync_issues_simple.py --dry-run

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

**Enhanced Features:**
- **Group-level summaries**: Shows statistics grouped by GitLab group
- **Progress tracking**: Real-time progress bars with operation counts
- **Safety checks**: Protected branch detection and confirmation prompts
- **Detailed logging**: Operation tracking with colored output

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

#### Interactive Menu Interface (NEW!)
```bash
# Launch interactive menu with numbered options
python glt_menu.py

# Direct access to specific tools:
# 1. Rename Branches
# 2. Generate Executive Dashboard  
# 3. Weekly Productivity Reports
# 4. Code Changes Reports
# 5. Project Analytics
# And more...
```

#### Weekly Productivity Reports (Enhanced!)
```bash
# Generate weekly report for specific groups and save as HTML
python scripts/weekly_reports.py --groups 1721,1267,1269 --output weekly_report.html

# Send email report to team (default: totrakool.k@thaibev.com)
python scripts/weekly_reports.py --groups 1721,1267,1269 --email team@company.com,manager@company.com

# Generate report for specific team members
python scripts/weekly_reports.py --groups 1721,1267,1269 --team john.doe,jane.smith --output report.json

# Generate 2-week report with email delivery
python scripts/weekly_reports.py --groups 1721,1267,1269 --weeks 2 --email team@company.com \
  --team-name "AI Development Team"

# Test email configuration
python scripts/weekly_reports.py --test-email your.email@company.com

# Generate report with attachments
python scripts/weekly_reports.py --groups 1721,1267,1269 --email team@company.com \
  --email-attachments "analytics.xlsx,metrics.pdf"

# Dry run mode (generate but don't send email)
python scripts/weekly_reports.py --groups 1721,1267,1269 --email team@company.com --dry-run
```

**Enhanced Analytics Features:**
- **Contributor Deduplication**: Maps multiple emails/usernames to unique contributors
- **Branch-Specific Metrics**: Three approaches for accurate branch analytics:
  - Total commits per branch
  - Unique commits (not shared with other branches)  
  - Git diff analysis for branch-specific changes
- **Date Filtering**: Client-side filtering ensures accurate weekly metrics
- **Active/Inactive Separation**: Clearly distinguishes projects with recent activity
- **Detailed Tables**: Group/Project/Branch and Group/Project/Contributor breakdowns
- **Person-Focused Views**: Contributor-first tables showing who works on what
- **Net Code Changes**: Lines added/removed with commit ownership tracking
- **Issue Tracking**: Issues opened/closed during the reporting period

#### Executive Dashboard Generation
```bash
# Generate dashboard for specific groups
python scripts/generate_executive_dashboard.py --groups 1721,1267,1269 --output dashboard.html

# Include specific time period
python scripts/generate_executive_dashboard.py --groups 1721 --days 30 --output monthly_dashboard.html

# Export as JSON for API consumption
python scripts/generate_executive_dashboard.py --groups 1721 --format json --output dashboard.json
```

#### Project Analytics
```bash
# Analyze single project
python scripts/analyze_projects.py project 123 --output analysis.json

# Analyze entire group
python scripts/analyze_projects.py group 456 --format markdown --output group_analysis.md

# Compare multiple projects
python scripts/analyze_projects.py compare 123,456,789 --output comparison.html

# Export to Excel
python scripts/export_analytics.py projects 123,456 --output analytics.xlsx
```

#### Code Changes Reports
```bash
# Generate code changes report for groups
python scripts/generate_code_changes_report.py --groups 1721,1267 --output report.html

# Include specific time period
python scripts/generate_code_changes_report.py --groups 1721 --days 30 --output monthly_changes.html

# Generate and automatically send via email
python scripts/generate_and_send_report.py --groups 1721,1267 --recipients team@company.com

# With custom email subject
python scripts/generate_and_send_report.py --groups 1721 --recipients manager@company.com \
  --subject "Weekly Code Activity Report"
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
  - `analytics.py`: Basic analytics functionality
  - `analytics_advanced.py`: Advanced analytics with health scoring
  - `group_enhancement.py`: Group-level operation enhancements

- **src/cli/**: CLI components for unified interface
  - `command_executor.py`: Executes CLI commands
  - `command_parser.py`: Natural language command parsing
  - `command_registry.py`: Registry of available commands
  - `help_system.py`: Interactive help system
  - `logging_config.py`: CLI-specific logging
  - `repl.py`: Interactive REPL functionality

- **src/utils/**: Shared utilities
  - `config.py`: Configuration management that merges YAML config with env variables
  - `logger.py`: Advanced logging with color support and operation tracking
  - `progress.py`: Progress bars and spinners for long operations
  - `validators.py`: Input validation for issues, projects, and files
  - `cache.py`: File-based caching for API responses

- **scripts/**: CLI entry points
  - `rename_branches.py`: Enhanced branch renaming with group-level summaries
  - `create_issues.py`: Full-featured issue creation with templates
  - `sync_issues.py`: Sync markdown files from issues folder to GitLab
  - `sync_issues_simple.py`: Pre-configured sync script for specific projects
  - `weekly_reports.py`: Advanced weekly reports with branch analytics and contributor insights
  - `generate_executive_dashboard.py`: Create executive dashboards with analytics
  - `generate_code_changes_report.py`: Generate code activity reports
  - `generate_and_send_report.py`: Combined report generation and email delivery
  - `analyze_projects.py`: Deep project and group analytics
  - `export_analytics.py`: Export analytics to Excel and other formats
  - `send_report_email.py`: Send HTML reports via email

- **glt_menu.py**: Interactive menu interface
  - Numbered options for all GitLab tools
  - Default email configuration (totrakool.k@thaibev.com)
  - Group ID selection with descriptions

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
8. **Timezone-Aware Processing**: All datetime operations use UTC with proper timezone handling
9. **Client-Side Data Filtering**: API responses are filtered client-side for accuracy
10. **Contributor Identity Normalization**: Multiple identities mapped to single contributors

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
6. **Use contributor deduplication** for accurate team metrics
7. **Apply client-side date filtering** for precise weekly reports

## Weekly Productivity Reports Features

### Core Capabilities
- **Advanced Branch Analytics**: Three-method analysis (git diff, ownership tracking, dual metrics)
- **Team Activity Metrics**: Commits, merge requests, issues across all repositories  
- **Project Health Scoring**: Automated health assessment with A-F grades
- **Individual Contributor Analytics**: Person-focused view with contributor deduplication
- **Executive Summary**: Key metrics and highlights with accurate date filtering
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

## Enhanced Branch Analytics

### Three-Method Analysis System
The weekly reports now provide three different approaches for analyzing branch-specific contributions:

#### 1. Git Diff Approach
Shows changes unique to each branch compared to its base branch using GitLab's Compare API:
```bash
# Shows only changes unique to feature branches
Lines±(Diff): +1,234  # Changes not in main branch
```

#### 2. Commit Ownership Method  
Tracks which branch first processed each commit to avoid double-counting:
```bash
# Example output showing ownership
| Branch | Total | Unique | Owned | Inherited |
|--------|-------|--------|-------|-----------|
| main   | 50    | 10     | 35    | 15        |
| feature| 45    | 5      | 15    | 30        |
```

#### 3. Dual Metrics Display
Provides both total and unique commit counts for comprehensive insight:
- **Total**: All commits on the branch
- **Unique**: Commits only on this branch (not shared with others)

### Contributor Analytics Enhancements

#### Person-Focused View
Contributors are now grouped alphabetically with all their projects listed together:
```bash
| Contributor     | Project              | Group      | Commits | MRs |
|-----------------|----------------------|------------|---------|-----|
| John Doe        | project-alpha        | AI-ML      | 25      | 3   |
| John Doe        | project-beta         | AI-ML      | 15      | 1   |
| Jane Smith      | project-gamma        | Research   | 30      | 5   |
```

#### Smart Filtering
- Removes pure issue-only entries (0 commits, 0 MRs, 0 lines) from active contributor tables
- Focuses on actual code contributions for clearer insights

#### Contributor Deduplication
Automatically maps multiple identities to single contributors:
```yaml
# Example mapping configuration
contributors:
  "Totrakool Khongsap":
    - "ta.khongsap@gmail.com"
    - "tkhongsap" 
    - "totrakool.k@thaibev.com"
```

### Implementation Details

#### Date Filtering
All metrics use client-side date filtering for accuracy:
```python
# Ensures commits are only counted within the specified week
if start_date <= commit_date <= end_date:
    commits.append(commit)
```

#### API Parameter Fixes
Corrected GitLab API calls for proper branch-specific data:
```python
# Fixed from params={} to direct parameters
commits = client._paginated_get(
    f'projects/{project_id}/repository/commits',
    since=start_date.isoformat(),
    until=end_date.isoformat(),
    ref=branch_name  # Correct parameter for branch-specific commits
)
```

## File-Based Issue Creation

### Overview
The file-based issue creation system allows creating GitLab issues from markdown or text files in the `issues/` folder. This approach is particularly useful for:
- Bulk issue creation
- Version-controlled issue templates
- Automated issue generation from other tools

### Supported Formats
1. **Markdown with YAML frontmatter** (recommended)
2. **Simple markdown** with hashtag labels
3. **Plain text** files

### curl vs API Methods
- **curl method** (default): Direct HTTP calls, no Python dependencies
- **API method** (`--use-api`): Uses GitLab Python client, better error handling

## Testing Strategy

### Test Organization
Tests are organized by module type:
- `tests/unit/api/` - API client tests
- `tests/unit/models/` - Data model tests
- `tests/unit/services/` - Service layer tests
- `tests/unit/scripts/` - CLI script tests
- `tests/unit/utils/` - Utility function tests

### Running Tests
The `run_tests.py` script provides a convenient way to run all tests with coverage reporting:

```bash
# Run all tests with coverage
python run_tests.py

# Run specific test suite
python run_tests.py tests/unit/api/

# Use pytest directly
pytest tests/unit/services/ -v

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

Individual test suites can be run for faster feedback during development.

## Setup Scripts

### Quick Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your GitLab URL and API token
```

### Installation via setup.py
```bash
# Install in development mode
pip install -e .

# Install for production
pip install .

# This adds console entry points:
# - glt (main CLI)
# - gitlab-rename-branches
# - gitlab-create-issues  
# - gitlab-analyze
```

