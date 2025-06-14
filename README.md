# GitLab Tools

Enhanced GitLab management tools for bulk operations, analytics, and automation.

## 🚀 Quick Start

Get productive with GitLab Tools in under 15 minutes! These three key features cover the most common workflows:

### 1. 🔄 Branch Renaming: Trunk to Main

Modernize your Git workflow by renaming branches across all repositories:

```bash
# Preview changes first (recommended)
python scripts/rename_branches.py --groups "AI-ML-Services" --dry-run

# Execute the rename operation  
python scripts/rename_branches.py --groups "AI-ML-Services" --old-branch trunk --new-branch main
```

**✅ Success indicators:**
```
✓ Successfully renamed: 15
⏭️ Skipped: 3  
❌ Failed: 0
```

### 2. 📊 Executive Dashboard & Email Reports

Generate beautiful analytics dashboards and deliver them via email:

```bash
# Generate dashboard for specific groups
python scripts/generate_executive_dashboard.py --groups 1721,1267,1269 --output dashboard.html

# Send the dashboard via email
python scripts/send_report_email.py dashboard.html manager@company.com "Weekly GitLab Analytics Report"
```

**✅ Success indicators:**
```
✅ Dashboard saved to: dashboard.html
   Total Projects: 25
   Active Projects: 20  
   Unique Contributors: 12
✅ Email sent successfully to: manager@company.com
```

### 3. 📝 Issue Creation from Files

Create GitLab issues in bulk from markdown files:

```bash
# Preview issues to be created
python scripts/sync_issues.py PROJECT_ID --dry-run

# Create issues from files in the issues/ folder
python scripts/sync_issues.py PROJECT_ID --issues-dir issues
```

**✅ Success indicators:**
```
Found 5 issue files to process
[1/5] Processing: user-authentication.md
  ✓ Issue created: #142
✓ Success: 5
❌ Failed: 0
```

---

**🎯 Ready for more?** Jump to detailed documentation:
- [Branch Renaming Details](#branch-renaming-trunk-to-main) 
- [Dashboard & Email Setup](#executive-dashboard--email-reports)
- [Issue Creation Guide](#issue-creation-from-files)
- [Complete Setup Guide](#prerequisites--setup)

## Features

### Core Features
- 🚀 **Bulk Branch Renaming** - Rename branches across multiple projects with safety checks
- 📊 **Repository Analytics** - Generate comprehensive metrics and reports for projects and groups
- 📝 **Issue Management** - Create issues from templates, CSV files, or interactively
- 🧪 **Comprehensive Testing** - Unit and integration tests with 80%+ coverage target
- 📈 **Progress Tracking** - Real-time progress bars and operation logging
- 🔒 **Safety Features** - Dry-run mode, protected branch detection, rollback support
- 📄 **Report Generation** - Export operations and analytics in Markdown, JSON, or text formats

### Advanced Analytics (New!)
- 📈 **Trend Analysis** - Analyze repository activity trends over time
- 🏥 **Health Scoring** - Automatic project health assessment with grades (A-F)
- 🤖 **Smart Recommendations** - AI-powered suggestions for improving project health
- 📊 **Project Comparison** - Compare multiple projects side-by-side
- 🌐 **HTML Dashboards** - Interactive web-based analytics dashboards
- 💾 **Smart Caching** - File-based caching for faster repeated queries
- 📑 **Excel Export** - Export analytics to Excel with multiple worksheets
- ⏱️ **Time-Series Analysis** - Track metrics evolution over custom time periods

## Scripts

### Core Scripts (Enhanced)

1. **scripts/rename_branches.py** - Enhanced branch renaming with safety features
   - Dry-run mode for preview
   - Protected branch detection
   - Progress tracking
   - Report generation
   - Configurable via YAML

2. **scripts/create_issues.py** - Advanced issue creation
   - Template-based creation
   - CSV bulk import
   - Interactive mode
   - Variable substitution

3. **scripts/analyze_projects.py** - GitLab analytics and reporting
   - Project and group metrics
   - Commit, branch, issue, and MR statistics
   - Contributor analytics
   - Multiple output formats

4. **scripts/sync_issues.py** - File-based issue creation
   - Read markdown/text files from issues folder
   - Support YAML frontmatter for metadata
   - Create issues using curl or API
   - Generate shell scripts for manual execution

### Legacy Scripts

1. **01_gitlab_info_extractor.py** - Extracts information about groups, subgroups, and projects
2. **02_gitlab_rename_trunk_to_main.py** - Original branch rename script
3. **03_create_gitlab_issues.py** - Original issue creation script

## 📋 Prerequisites & Setup

### System Requirements

- **Python 3.8 or higher**
- **Git** (for repository operations)
- **curl** (for alternative API calls)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/tkhongsap/tcctech-gitlab.git
cd tcctech-gitlab

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create your environment configuration file:

```bash
cp .env.example .env
```

Edit the `.env` file with your GitLab credentials:

```bash
# GitLab Configuration
GITLAB_URL=https://your-gitlab-instance.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx

# Email Configuration (for dashboard reports)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@company.com
SMTP_FROM_NAME=GitLab Analytics

# Optional: Override dry-run behavior
GITLAB_DRY_RUN=false
```

### 3. GitLab API Token Setup

Your GitLab API token needs these permissions:

- ✅ **api** - Full API access
- ✅ **read_repository** - Read repository information
- ✅ **read_user** - Read user information

**To create an API token:**
1. Go to your GitLab instance → User Settings → Access Tokens
2. Create a new token with the required scopes
3. Copy the token to your `.env` file

### 4. Setup Validation

Verify your configuration is working:

```bash
# Test GitLab connectivity
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('GitLab URL:', os.getenv('GITLAB_URL'))
print('Token configured:', 'Yes' if os.getenv('GITLAB_TOKEN') else 'No')
"

# Test a simple API call
python scripts/analyze_projects.py --help
```

**✅ Expected output:**
```
GitLab URL: https://your-gitlab-instance.com
Token configured: Yes
usage: analyze_projects.py [-h] [--project PROJECT] [--group GROUP] ...
```

### 5. Email Configuration (Optional)

For dashboard email delivery, configure SMTP settings. **Gmail users:**

1. Enable 2-factor authentication
2. Generate an app password: Account → Security → App passwords
3. Use the app password as `SMTP_PASSWORD`

**Test email configuration:**
```bash
echo "<h1>Test Email</h1>" > test.html
python scripts/send_report_email.py test.html your-email@company.com "Test Subject"
rm test.html
```

## 🔧 Key Features

### 🔄 Branch Renaming: Trunk to Main

**Purpose:** Modernize your Git workflow by safely renaming branches across multiple repositories with comprehensive safety checks and rollback support.

**Use Cases:**
- Migrate from legacy "trunk" to modern "main" branch naming
- Standardize branch naming across all repositories  
- Bulk rename operations with safety guarantees

#### Prerequisites
- GitLab API token with `api` scope
- Groups configured in `config/config.yaml` or use `--groups` parameter
- Repositories should not have active merge requests targeting the old branch

#### Step-by-Step Instructions

**1. Preview Changes (Always Start Here)**
```bash
# Preview changes for specific groups
python scripts/rename_branches.py --groups "AI-ML-Services" "Research Repos" --dry-run

# Preview with report generation
python scripts/rename_branches.py --groups "AI-ML-Services" --dry-run --report reports/rename-preview.md
```

**2. Execute Rename Operation**
```bash
# Rename trunk to main for specified groups
python scripts/rename_branches.py --groups "AI-ML-Services" --old-branch trunk --new-branch main

# Custom branch names
python scripts/rename_branches.py --groups "AI-ML-Services" --old-branch develop --new-branch main
```

#### Configuration Options

**Command Line Arguments:**
- `--old-branch` / `-o` - Current branch name (default: trunk)
- `--new-branch` / `-n` - New branch name (default: main)  
- `--groups` / `-g` - Groups to process (space-separated)
- `--dry-run` - Preview changes without executing
- `--config` / `-c` - Path to configuration file
- `--report` - Generate operation report (.md, .json, .txt)
- `--log-level` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)

**Configuration File (`config/config.yaml`):**
```yaml
gitlab:
  rate_limit: 3
  timeout: 30

branch_operations:
  skip_protected: true
  update_merge_requests: true

groups:
  - name: "AI-ML-Services"
    filters:
      exclude_archived: true
```

#### Safety Features
- **Protected Branch Detection** - Automatically skips protected branches
- **Existence Checks** - Verifies old branch exists and new branch doesn't
- **Dry-Run Mode** - Preview all changes before execution
- **Progress Tracking** - Real-time feedback on operation status
- **Rollback Support** - Detailed logs for manual rollback if needed

#### Expected Outputs

**Dry-Run Success:**
```
Branch Rename Tool: 'trunk' -> 'main'
Running in DRY RUN mode - no changes will be made

Processing group: AI-ML-Services
Found 15 projects in group 'AI-ML-Services'
[1/15] Processing: project-alpha
[DRY RUN] Would rename 'trunk' to 'main'

Operation Summary
=================
Total projects processed: 15
✓ Successfully renamed: 12
⏭️ Skipped: 3
❌ Failed: 0
```

#### Troubleshooting

**Common Issues:**
- **"Branch 'trunk' not found"** - Project doesn't have the old branch, operation skipped
- **"Branch 'main' already exists"** - Target branch exists, operation skipped
- **"Branch is protected"** - Protected branches are skipped for safety
- **API rate limit exceeded** - Increase `rate_limit` in config or wait

**Recovery:**
- All operations are logged in detail
- Use `--report` flag to generate comprehensive operation reports
- Check GitLab project settings for branch protection rules

### 📊 Executive Dashboard & Email Reports

**Purpose:** Generate beautiful, interactive analytics dashboards for GitLab projects and automatically deliver them to stakeholders via email.

**Use Cases:**
- Weekly/monthly executive reporting
- Project health monitoring and alerts
- Team performance analytics and insights
- Automated stakeholder communication

#### Prerequisites
- GitLab API token with `read_repository` and `read_user` scopes
- GitLab group IDs for the projects you want to analyze
- SMTP configuration for email delivery (optional)

#### Data Requirements
The dashboard analyzes and presents:
- **Project Health Scores** - A-F grades based on activity, issues, collaboration
- **Commit Activity** - Trends, contributor statistics, code frequency
- **Issue Management** - Open/closed ratios, aging analysis, priority distribution
- **Team Performance** - Individual contributions, workload analysis
- **Technology Stack** - Language usage, repository insights

#### Step-by-Step Instructions

**1. Generate Dashboard**
```bash
# Basic dashboard for specific groups
python scripts/generate_executive_dashboard.py --groups 1721,1267,1269

# Custom analysis period and output
python scripts/generate_executive_dashboard.py \
  --groups 1721,1267,1269 \
  --days 60 \
  --output weekly_report.html \
  --team-name "AI Development Team"
```

**2. Send Dashboard via Email**
```bash
# Send to single recipient
python scripts/send_report_email.py weekly_report.html manager@company.com "Weekly Analytics Report"

# Complete workflow with variables
REPORT_FILE="executive_dashboard_$(date +%Y%m%d).html"
python scripts/generate_executive_dashboard.py --groups 1721,1267,1269 --output "$REPORT_FILE"
python scripts/send_report_email.py "$REPORT_FILE" "team@company.com" "Weekly GitLab Report - $(date +%B %d)"
```

#### Configuration Options

**Dashboard Generation Arguments:**
- `--groups` / `-g` - Comma-separated GitLab group IDs (required)
- `--output` / `-o` - Output HTML file path (default: executive_dashboard.html)
- `--days` - Analysis period in days (default: 30)
- `--team-name` - Team name for report header (default: Development Team)

**Email Delivery Arguments:**
- `html_file` - Path to HTML dashboard file
- `recipient` - Email address to send to
- `subject` - Email subject line

**Environment Variables:**
```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com          # SMTP server address
SMTP_PORT=587                       # SMTP port
SMTP_USERNAME=your-email@company.com # SMTP username
SMTP_PASSWORD=your-app-password      # SMTP password
SMTP_FROM_EMAIL=your-email@company.com # From address
SMTP_FROM_NAME=GitLab Analytics      # From display name
```

#### Dashboard Features
- **Modern shadcn/ui Design** - Professional, clean interface
- **Interactive Components** - Clickable charts, sortable tables
- **Health Scoring System** - Automated project health assessment
- **AI Recommendations** - Smart suggestions for improving project health
- **Responsive Layout** - Works on desktop and mobile
- **Export Ready** - Perfect for printing or PDF conversion

#### Expected Outputs

**Dashboard Generation Success:**
```
🚀 Starting executive dashboard generation...
   Analyzing 3 groups over 30 days

✅ Dashboard saved to: executive_dashboard.html

📊 Analysis Summary:
   Total Projects: 25
   Active Projects: 20
   Total Commits: 1,250
   Unique Contributors: 12
   Health Distribution: A+(2) A(8) B(7) C(6) D(2)
```

**Email Delivery Success:**
```
✅ Email sent successfully to: manager@company.com
```

#### Scheduling & Automation

**Weekly Reports with Cron:**
```bash
# Add to crontab (crontab -e)
0 9 * * MON cd /path/to/gitlab-tools && ./scripts/weekly_dashboard.sh
```

**Example Automation Script (`weekly_dashboard.sh`):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
REPORT="weekly_dashboard_$DATE.html"

# Generate dashboard
python scripts/generate_executive_dashboard.py \
  --groups 1721,1267,1269 \
  --days 7 \
  --output "$REPORT" \
  --team-name "Development Team"

# Send to multiple recipients
for email in manager@company.com team-lead@company.com cto@company.com; do
  python scripts/send_report_email.py "$REPORT" "$email" "Weekly GitLab Report - $(date +%B %d)"
done

# Cleanup old reports (keep last 10)
ls -t weekly_dashboard_*.html | tail -n +11 | xargs rm -f
```

#### Troubleshooting

**Common Issues:**
- **"Missing GITLAB_TOKEN"** - Set GITLAB_TOKEN or GITLAB_API_TOKEN in .env
- **"Group not found"** - Verify group IDs are correct and accessible
- **"Email sending failed"** - Check SMTP credentials and server settings
- **Empty dashboard** - Verify groups contain projects with recent activity

**Performance Tips:**
- Use smaller `--days` values for faster generation
- Groups with 50+ projects may take 2-3 minutes to analyze
- Large reports (>5MB) may have email delivery limits

### 📝 Issue Creation from Files

**Purpose:** Create GitLab issues in bulk from markdown and text files with smart metadata extraction and flexible file format support.

**Use Cases:**
- Convert planning documents into trackable issues
- Bulk import issues from external systems
- Template-based issue creation workflows
- Collaborative issue creation via file sharing

#### Prerequisites
- GitLab API token with project access
- GitLab project ID or path
- Issue files in supported formats (.md, .txt, .markdown)

#### File Format Support

**🏆 YAML Frontmatter (Recommended)** - Full metadata support:
```markdown
---
title: Implement User Authentication
labels: [feature, security, high-priority]
assignee: john.doe
milestone: v1.0
due_date: 2024-02-01
weight: 8
priority: high
---

## Description
Implement secure user authentication with OAuth support.

## Requirements
- User registration with email verification
- Login/logout functionality
- Password reset via email
- OAuth integration (Google, Facebook)

## Acceptance Criteria
- [ ] User can register with email/password
- [ ] Email verification required
- [ ] Session management implemented

#backend #api #authentication
```

**📝 Simple Markdown** - Auto-extracts title and labels:
```markdown
# Fix Login Bug

Users cannot login after recent deployment. The session cookie is not being set properly.

**Steps to reproduce:**
1. Navigate to login page
2. Enter valid credentials
3. Click login button

**Expected:** User logged in successfully
**Actual:** Session cookie not set, user remains logged out

#bug #critical #authentication
```

**📄 Plain Text** - Uses filename as title:
```
Add Dark Mode Support

Implement a toggle for dark mode in user preferences. Should persist across sessions and apply to all UI components.

Labels: feature, ui, enhancement
Assignee: ui-team
```

#### Step-by-Step Instructions

**1. Prepare Issue Files**
```bash
# Create issues directory
mkdir -p issues

# Add your issue files (see format examples above)
# Files can be .md, .txt, or .markdown
```

**2. Preview Issues (Recommended)**
```bash
# Preview all issues to be created
python scripts/sync_issues.py PROJECT_ID --dry-run

# Preview with custom directory
python scripts/sync_issues.py PROJECT_ID --issues-dir my-issues --dry-run
```

**3. Create Issues**
```bash
# Create issues using GitLab API
python scripts/sync_issues.py PROJECT_ID --use-api

# Create issues using curl (alternative method)
python scripts/sync_issues.py PROJECT_ID

# Custom issues directory
python scripts/sync_issues.py PROJECT_ID --issues-dir sprint-planning
```

#### Configuration Options

**Command Line Arguments:**
- `project` - GitLab project ID or path (required)
- `--issues-dir` - Directory containing issue files (default: issues)
- `--use-api` - Use GitLab API directly instead of curl
- `--dry-run` - Preview issues without creating them
- `--generate-script` - Generate shell script with curl commands
- `--config` - Configuration file path

**Supported Metadata Fields:**
- `title` - Issue title (auto-extracted if not provided)
- `labels` - Issue labels (array or comma-separated)
- `assignee` - Username to assign issue to
- `milestone` - Milestone name or ID
- `due_date` - Due date (YYYY-MM-DD format)
- `weight` - Issue weight (1-10)
- `priority` - Priority level (custom field)

#### Smart Parsing Features
- **Auto Title Extraction** - Uses first heading or filename
- **Hashtag Labels** - Converts #hashtags to labels automatically
- **Metadata from Content** - Extracts "Labels:", "Assignee:" from plain text
- **Duplicate Prevention** - Won't create duplicate issues
- **File Validation** - Checks file syntax and required fields

#### Expected Outputs

**Dry-Run Preview:**
```
GitLab URL: https://gitlab.company.com
Project: my-project
Issues directory: issues
Mode: API

🔍 DRY RUN MODE - No issues will be created

Found 5 issue files to process

[1/5] Processing: user-authentication.md
  Title: Implement User Authentication
  Labels: feature, security, high-priority
  ✓ Preview: Would create issue

[2/5] Processing: fix-login-bug.md
  Title: Fix Login Bug  
  Labels: bug, critical, authentication
  ✓ Preview: Would create issue

SUMMARY
=======
Total files: 5
✓ Would create: 5
✗ Would fail: 0
```

**Successful Creation:**
```
[1/5] Processing: user-authentication.md
  Title: Implement User Authentication
  Labels: feature, security, high-priority
  ✓ Issue created: #142

[2/5] Processing: fix-login-bug.md  
  Title: Fix Login Bug
  Labels: bug, critical, authentication
  ✓ Issue created: #143

SUMMARY
=======
Total files: 5
✓ Success: 5
✗ Failed: 0
```

#### Advanced Usage

**Generate Shell Script for Manual Execution:**
```bash
# Generate script with curl commands
python scripts/sync_issues.py PROJECT_ID --generate-script

# Creates: issues/create_issues.sh
chmod +x issues/create_issues.sh
./issues/create_issues.sh
```

**Batch Processing Multiple Projects:**
```bash
# Process same issues for multiple projects
for project in project-1 project-2 project-3; do
  echo "Processing $project..."
  python scripts/sync_issues.py "$project" --issues-dir templates/sprint-1
done
```

#### Troubleshooting

**Common Issues:**
- **"No issue files found"** - Check directory path and file extensions
- **"YAML parsing failed"** - Verify frontmatter syntax (3 dashes above/below)
- **"Project not found"** - Verify project ID/path and API token permissions
- **"Missing title"** - Ensure files have headings or YAML title field

**File Validation:**
```bash
# Check file syntax before processing
python -c "
import yaml
with open('issues/my-issue.md') as f:
    content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        yaml.safe_load(parts[1])
        print('✓ Valid YAML frontmatter')
"
```

### Analytics and Reporting

#### Basic Analytics
```bash
# Analyze a single project
python scripts/analyze_projects.py --project my-project

# Analyze an entire group
python scripts/analyze_projects.py --group "AI-ML-Services"

# Generate different formats
python scripts/analyze_projects.py --project my-project --format json -o report.json
python scripts/analyze_projects.py --group my-group --format markdown -o report.md
```

#### Advanced Analytics
```bash
# Trend analysis with health scoring
python scripts/analyze_projects.py --project my-project --trends --days 90

# Compare multiple projects
python scripts/analyze_projects.py --compare project1 project2 project3

# Generate HTML dashboard
python scripts/analyze_projects.py --project my-project --trends --html -o dashboard.html

# Use caching for faster repeated queries
python scripts/analyze_projects.py --project my-project  # First run caches data
python scripts/analyze_projects.py --project my-project  # Uses cached data

# Clear cache if needed
python scripts/analyze_projects.py --project my-project --clear-cache
```

#### Export to Excel
```bash
# Export project analytics to Excel
python scripts/export_analytics.py my-project -o project_report.xlsx

# Export group analytics
python scripts/export_analytics.py "AI-ML-Services" -o group_report.xlsx

# Compare projects in Excel
python scripts/export_analytics.py "compare:1,2,3" -o comparison.xlsx

# Include trend analysis
python scripts/export_analytics.py my-project --trends --days 60 -o trends.xlsx
```

### Legacy Scripts

The original scripts are still available:

```bash
# Extract GitLab information
python 01_gitlab_info_extractor.py

# Rename trunk to main (original version)
python 02_gitlab_rename_trunk_to_main.py

# Create issues from text file
python 03_create_gitlab_issues.py [project_name] [issues_file]
```

## Testing

Run the test suite:

```bash
# Run all tests with coverage
pytest

# Run only unit tests
pytest tests/unit -v

# Run with specific coverage threshold
pytest --cov-fail-under=80

# Generate HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

## ⚙️ Configuration Examples

### Configuration Hierarchy

GitLab Tools uses a flexible configuration system with three levels (highest priority first):

1. **Command Line Arguments** - Override everything
2. **Environment Variables** - Override configuration files  
3. **Configuration Files** - Default settings (`config/config.yaml`)

### Environment Variables Reference

Create a `.env` file in the project root with these variables:

```bash
# Required Configuration
GITLAB_URL=https://your-gitlab-instance.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx

# Email Configuration (for dashboard reports)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@company.com
SMTP_FROM_NAME=GitLab Analytics

# Feature Toggles (Optional)
GITLAB_DRY_RUN=false
GITLAB_COLORED_OUTPUT=true
GITLAB_SHOW_PROGRESS=true
GITLAB_CONCURRENT_WORKERS=5

# Logging (Optional)
LOG_LEVEL=INFO
LOG_FILE=logs/gitlab-tools.log

# API Settings (Optional)
GITLAB_RATE_LIMIT=3
GITLAB_TIMEOUT=30
GITLAB_VERIFY_SSL=true
```

### Configuration File Examples

**Complete `config/config.yaml` for different environments:**

**Development Environment:**
```yaml
gitlab:
  rate_limit: 5  # Higher rate for dev
  timeout: 60
  verify_ssl: false  # For self-signed certs

features:
  dry_run: true  # Safe default for dev
  show_progress: true
  colored_output: true
  concurrent_workers: 3

branch_operations:
  skip_protected: true
  update_merge_requests: false

groups:
  - name: "Development Projects"
    filters:
      exclude_archived: true
      min_activity_days: 7

logging:
  level: DEBUG
  file: "logs/dev.log"
```

**Production Environment:**
```yaml
gitlab:
  rate_limit: 2  # Conservative for prod
  timeout: 30
  verify_ssl: true
  retry_count: 5

features:
  dry_run: false
  backup: true
  show_progress: false  # For CI/CD
  colored_output: false
  concurrent_workers: 8

branch_operations:
  skip_protected: true
  update_merge_requests: true

groups:
  - name: "AI-ML-Services"
    filters:
      exclude_archived: true
      min_activity_days: 30
  - name: "Research Repos"
    filters:
      exclude_archived: true
      min_activity_days: 60

logging:
  level: INFO
  file: "logs/production.log"
  max_size: 50
  backup_count: 10

output:
  directory: "/var/log/gitlab-reports"
  formats: ["json", "markdown"]
```

**CI/CD Environment:**
```yaml
gitlab:
  rate_limit: 1
  timeout: 120
  retry_count: 3

features:
  dry_run: false
  show_progress: false
  colored_output: false
  concurrent_workers: 2

logging:
  level: WARNING
  format: "%(levelname)s: %(message)s"
```

### Feature-Specific Configuration

**Branch Renaming Configuration:**
```yaml
branch_operations:
  default_old_branch: "develop"  # Custom old branch
  default_new_branch: "main"
  skip_protected: true
  update_merge_requests: true
  
  # Safety settings
  require_confirmation: true
  create_backup_refs: true
```

**Dashboard Configuration:**
```yaml
dashboard:
  default_days: 30
  health_thresholds:
    excellent: 90
    good: 75
    fair: 60
  exclude_inactive_days: 90
  
  # Email settings
  default_recipients:
    - "manager@company.com"
    - "team-lead@company.com"
```

**Issue Creation Configuration:**
```yaml
issue_operations:
  default_labels: ["automated", "from-file"]
  template_dir: "templates/issues"
  add_timestamp: true
  
  # Auto-assignment rules
  assignee_mapping:
    "feature": "dev-team"
    "bug": "qa-team"
    "security": "security-team"
```

### Environment-Specific Considerations

**🔧 Development:**
- Use `dry_run: true` by default
- Enable debug logging and progress bars
- Use shorter timeouts for faster feedback
- Consider using test GitLab instance

**🚀 Production:**
- Enable backups before destructive operations
- Use conservative rate limits
- Disable colored output for clean logs
- Configure proper log rotation

**🤖 CI/CD:**
- Disable interactive features
- Use minimal logging (WARNING level)
- Set longer timeouts for reliability
- Use service accounts with limited permissions

## 📖 Command Reference

### Branch Renaming Commands

```bash
# Basic Usage
python scripts/rename_branches.py --groups "Group Name" [OPTIONS]

# All Available Options
--old-branch, -o        Current branch name (default: trunk)
--new-branch, -n        New branch name (default: main)
--groups, -g           Groups to process (space-separated)
--dry-run              Preview changes without executing
--config, -c           Path to configuration file
--report               Generate report file (.md, .json, .txt)
--log-level            Logging level (DEBUG, INFO, WARNING, ERROR)
--no-color            Disable colored output

# Examples
python scripts/rename_branches.py --groups "AI-ML-Services" --dry-run
python scripts/rename_branches.py --groups "AI-ML-Services" "Research Repos" 
python scripts/rename_branches.py --old-branch develop --new-branch main --report rename-report.md
```

### Dashboard Generation Commands

```bash
# Basic Usage
python scripts/generate_executive_dashboard.py --groups GROUP_IDS [OPTIONS]

# All Available Options
--groups, -g           Comma-separated GitLab group IDs (required)
--output, -o           Output HTML file path (default: executive_dashboard.html)
--days                 Analysis period in days (default: 30)
--team-name           Team name for report header (default: Development Team)

# Examples
python scripts/generate_executive_dashboard.py --groups 1721,1267,1269
python scripts/generate_executive_dashboard.py --groups 1721 --days 60 --output monthly-report.html
python scripts/generate_executive_dashboard.py --groups 1721,1267 --team-name "AI Research Team"
```

### Email Delivery Commands

```bash
# Basic Usage
python scripts/send_report_email.py HTML_FILE RECIPIENT SUBJECT

# Examples
python scripts/send_report_email.py dashboard.html manager@company.com "Weekly Report"
python scripts/send_report_email.py report.html "team@company.com" "Monthly Analytics - $(date +%B)"
```

### Issue Creation Commands

```bash
# Basic Usage
python scripts/sync_issues.py PROJECT_ID [OPTIONS]

# All Available Options
--issues-dir           Directory containing issue files (default: issues)
--use-api             Use GitLab API instead of curl
--dry-run             Preview issues without creating them
--generate-script     Generate shell script with curl commands
--config              Configuration file path

# Examples
python scripts/sync_issues.py my-project --dry-run
python scripts/sync_issues.py 123 --issues-dir sprint-planning --use-api
python scripts/sync_issues.py my-project --generate-script
```

## 🔄 Workflow Integration

### End-to-End Workflows

**🎯 Weekly Executive Reporting Workflow:**
```bash
#!/bin/bash
# weekly-report.sh - Complete executive reporting workflow

DATE=$(date +%Y%m%d)
REPORT_FILE="executive_dashboard_$DATE.html"

echo "🚀 Starting weekly executive report generation..."

# 1. Generate comprehensive dashboard
python scripts/generate_executive_dashboard.py \
  --groups 1721,1267,1269 \
  --days 7 \
  --output "$REPORT_FILE" \
  --team-name "Development Team"

# 2. Send to stakeholders
RECIPIENTS=(
  "cto@company.com"
  "vp-engineering@company.com" 
  "team-leads@company.com"
)

for recipient in "${RECIPIENTS[@]}"; do
  echo "📧 Sending report to $recipient..."
  python scripts/send_report_email.py \
    "$REPORT_FILE" \
    "$recipient" \
    "Weekly Development Report - $(date +%B %d, %Y)"
done

# 3. Archive report
mkdir -p "archives/$(date +%Y/%m)"
cp "$REPORT_FILE" "archives/$(date +%Y/%m)/"

echo "✅ Weekly report workflow completed!"
```

**🔧 Repository Modernization Workflow:**
```bash
#!/bin/bash
# modernize-repos.sh - Comprehensive repository modernization

echo "🔄 Starting repository modernization workflow..."

# 1. Preview branch renaming across all groups
echo "📋 Generating preview report..."
python scripts/rename_branches.py \
  --groups "AI-ML-Services" "Research Repos" "Internal Services" \
  --dry-run \
  --report "reports/modernization-preview.md"

echo "📖 Review the preview report: reports/modernization-preview.md"
read -p "Proceed with branch renaming? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
  # 2. Execute branch renaming
  echo "🚀 Executing branch renaming..."
  python scripts/rename_branches.py \
    --groups "AI-ML-Services" "Research Repos" "Internal Services" \
    --report "reports/modernization-results.md"
  
  # 3. Generate completion report
  echo "📊 Generating completion dashboard..."
  python scripts/generate_executive_dashboard.py \
    --groups 1721,1267,1269 \
    --output "modernization-complete.html" \
    --team-name "Modernization Team"
  
  # 4. Notify team
  python scripts/send_report_email.py \
    "modernization-complete.html" \
    "engineering@company.com" \
    "Repository Modernization Complete - $(date +%B %d)"
  
  echo "✅ Repository modernization completed!"
else
  echo "❌ Modernization cancelled"
fi
```

**📝 Sprint Planning Workflow:**
```bash
#!/bin/bash
# sprint-planning.sh - Convert planning docs to GitLab issues

SPRINT="sprint-$(date +%Y-%U)"
PROJECTS=("project-alpha" "project-beta" "project-gamma")

echo "📝 Starting sprint planning workflow for $SPRINT..."

# 1. Validate issue files
echo "🔍 Validating issue files..."
if [ ! -d "planning/$SPRINT" ]; then
  echo "❌ Planning directory not found: planning/$SPRINT"
  exit 1
fi

# 2. Preview issues for each project
for project in "${PROJECTS[@]}"; do
  echo "📋 Previewing issues for $project..."
  python scripts/sync_issues.py "$project" \
    --issues-dir "planning/$SPRINT" \
    --dry-run
done

# 3. Create issues if preview looks good
read -p "Create issues for all projects? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
  for project in "${PROJECTS[@]}"; do
    echo "🚀 Creating issues for $project..."
    python scripts/sync_issues.py "$project" \
      --issues-dir "planning/$SPRINT" \
      --use-api
  done
  
  echo "✅ Sprint planning completed for $SPRINT!"
else
  echo "❌ Issue creation cancelled"
fi
```

### Feature Integration Examples

**🔗 Combining All Three Features:**
```bash
#!/bin/bash
# complete-project-setup.sh - Full project modernization and reporting

PROJECT_GROUP="New Product Team"
GROUP_ID=1234

echo "🚀 Complete project setup workflow..."

# Step 1: Modernize branch structure
echo "1️⃣ Modernizing branch structure..."
python scripts/rename_branches.py \
  --groups "$PROJECT_GROUP" \
  --old-branch master \
  --new-branch main \
  --report "setup-branches.md"

# Step 2: Import initial issues from planning docs
echo "2️⃣ Importing initial project issues..."
python scripts/sync_issues.py new-product-project \
  --issues-dir "project-setup/initial-issues" \
  --use-api

# Step 3: Generate baseline dashboard
echo "3️⃣ Generating project baseline dashboard..."
python scripts/generate_executive_dashboard.py \
  --groups $GROUP_ID \
  --output "project-baseline.html" \
  --team-name "$PROJECT_GROUP"

# Step 4: Send setup summary to stakeholders
echo "4️⃣ Notifying stakeholders..."
python scripts/send_report_email.py \
  "project-baseline.html" \
  "stakeholders@company.com" \
  "New Project Setup Complete - $PROJECT_GROUP"

echo "✅ Complete project setup finished!"
```

### Automation & Scheduling

**⏰ Cron Job Examples:**
```bash
# Add to crontab (crontab -e)

# Daily health check dashboard (weekdays at 9 AM)
0 9 * * 1-5 cd /path/to/gitlab-tools && python scripts/generate_executive_dashboard.py --groups 1721,1267,1269 --days 1 --output daily-health.html

# Weekly comprehensive report (Mondays at 8 AM)
0 8 * * 1 cd /path/to/gitlab-tools && bash scripts/weekly-report.sh

# Monthly modernization check (1st of month at 6 AM)
0 6 1 * * cd /path/to/gitlab-tools && python scripts/rename_branches.py --groups "All Groups" --dry-run --report monthly-branch-check.md
```

**🐳 Docker Integration:**
```bash
# Run in Docker for CI/CD environments
docker run --rm \
  -v "$(pwd):/workspace" \
  -v "$(pwd)/.env:/workspace/.env:ro" \
  gitlab-tools:latest \
  python scripts/generate_executive_dashboard.py \
  --groups 1721,1267,1269 \
  --output /workspace/dashboard.html
```

## ✅ Success Validation

### Verification Steps

**🔍 Setup Validation Checklist:**
```bash
# 1. Test GitLab connectivity
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('✓ GitLab URL:', os.getenv('GITLAB_URL'))
print('✓ Token configured:', 'Yes' if os.getenv('GITLAB_TOKEN') else 'No')
"

# 2. Test API access
python scripts/analyze_projects.py --help > /dev/null && echo "✓ Scripts executable"

# 3. Test email configuration (if configured)
echo "<h1>Test</h1>" > test.html
python scripts/send_report_email.py test.html your-email@company.com "Test" && echo "✓ Email working"
rm test.html

# 4. Test dry-run operations
python scripts/rename_branches.py --groups "Test Group" --dry-run > /dev/null && echo "✓ Branch rename ready"
python scripts/sync_issues.py test-project --dry-run --issues-dir issues > /dev/null && echo "✓ Issue sync ready"
```

### Expected Outputs & Interpretation

**✅ Successful Branch Rename:**
```
Branch Rename Tool: 'trunk' -> 'main'
Processing group: AI-ML-Services
Found 15 projects in group 'AI-ML-Services'

Operation Summary
=================
Total projects processed: 15
✓ Successfully renamed: 12    ← Good: Most projects processed
⏭️ Skipped: 3                ← Normal: Some projects may not have old branch
❌ Failed: 0                 ← Excellent: No failures
```

**✅ Successful Dashboard Generation:**
```
🚀 Starting executive dashboard generation...
   Analyzing 3 groups over 30 days

✅ Dashboard saved to: executive_dashboard.html

📊 Analysis Summary:
   Total Projects: 25          ← Shows scope
   Active Projects: 20         ← 80% active is healthy
   Total Commits: 1,250        ← Good activity level
   Unique Contributors: 12     ← Healthy team size
   Health Distribution: A+(2) A(8) B(7) C(6) D(2)  ← Most projects healthy
```

**✅ Successful Issue Creation:**
```
Found 5 issue files to process

[1/5] Processing: user-authentication.md
  Title: Implement User Authentication
  Labels: feature, security, high-priority
  ✓ Issue created: #142        ← Successful creation with issue number

SUMMARY
=======
Total files: 5
✓ Success: 5                  ← 100% success rate
❌ Failed: 0
```

### Troubleshooting Guide

**🔧 Common Issues & Solutions:**

| Problem | Symptoms | Solution |
|---------|----------|----------|
| **API Token Issues** | "401 Unauthorized" errors | Verify token in .env, check permissions |
| **Group Not Found** | "Group 'X' not found" | Verify group name/ID, check access permissions |
| **Rate Limiting** | "429 Too Many Requests" | Reduce `rate_limit` in config, wait before retry |
| **Email Failures** | "Email sending failed" | Check SMTP settings, verify credentials |
| **Empty Dashboard** | Dashboard shows no data | Verify groups have recent activity, check date range |
| **File Parsing Errors** | "YAML parsing failed" | Check frontmatter syntax, validate with YAML parser |

**🩺 Health Check Commands:**
```bash
# Check GitLab API connectivity
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "$GITLAB_URL/api/v4/user"

# Validate configuration file
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Test SMTP connection
python -c "
import smtplib, ssl, os
from dotenv import load_dotenv
load_dotenv()
context = ssl.create_default_context()
with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT', 587))) as server:
    server.starttls(context=context)
    server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
    print('✓ SMTP connection successful')
"
```

**📋 Performance Optimization:**
- Use smaller `--days` values for faster dashboard generation
- Enable caching for repeated API calls
- Run operations during off-peak hours
- Use `--dry-run` first to estimate operation time

### Log Interpretation

**📊 Understanding Log Levels:**
- **DEBUG** - Detailed API calls and internal operations
- **INFO** - Normal operation progress and results
- **WARNING** - Non-critical issues (skipped items, retries)
- **ERROR** - Failed operations requiring attention
- **CRITICAL** - System-level failures

**Example Log Analysis:**
```
2024-01-15 10:30:15 - INFO - Processing group: AI-ML-Services
2024-01-15 10:30:16 - INFO - Found 15 projects in group
2024-01-15 10:30:17 - WARNING - Branch 'trunk' not found in project-alpha  ← Expected
2024-01-15 10:30:18 - INFO - [DRY RUN] Would rename 'trunk' to 'main'      ← Safe preview
2024-01-15 10:30:19 - ERROR - API rate limit exceeded, retrying...          ← Needs attention
```

## Project Structure

```
gitlab-tools/
├── src/                    # Core library code
│   ├── api/               # GitLab API client
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── scripts/               # CLI scripts
├── templates/             # Issue templates
│   └── issues/
│       ├── epic.yaml
│       ├── feature.yaml
│       └── bug.yaml
├── tests/                 # Test suite
│   ├── unit/
│   └── integration/
├── config/                # Configuration
│   └── config.yaml
└── docs/                  # Documentation
```

## Documentation

- [Analytics Guide](docs/ANALYTICS_GUIDE.md) - Comprehensive guide to analytics features
- [API Reference](docs/API_REFERENCE.md) - API client documentation (coming soon)
- [Development Guide](docs/DEVELOPMENT.md) - Contributing and development setup (coming soon)

## Requirements

- Python 3.8 or higher
- Required packages: See `requirements.txt`

### Core Dependencies
- `requests` - HTTP library for GitLab API
- `python-dotenv` - Environment variable management
- `PyYAML` - Configuration file support
- `click` - CLI framework
- `rich` - Terminal formatting

### Analytics Dependencies
- `pandas` - Data analysis
- `matplotlib` - Visualization
- `openpyxl` - Excel export

## Installation

```bash
# Clone the repository
git clone https://github.com/tkhongsap/tcctech-gitlab.git
cd tcctech-gitlab

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your GitLab credentials
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 