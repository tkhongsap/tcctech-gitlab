# GitLab Tools

Enhanced GitLab management tools for bulk operations, analytics, and automation.

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

### Legacy Scripts

1. **01_gitlab_info_extractor.py** - Extracts information about groups, subgroups, and projects
2. **02_gitlab_rename_trunk_to_main.py** - Original branch rename script
3. **03_create_gitlab_issues.py** - Original issue creation script

## Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd gitlab-tools
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your GitLab credentials:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file and add your GitLab URL and API token.

## Usage

### Branch Renaming (Enhanced)

```bash
# Dry run mode (preview changes)
python scripts/rename_branches.py --dry-run

# Rename specific branches
python scripts/rename_branches.py --old-branch develop --new-branch main

# Process specific groups
python scripts/rename_branches.py --groups "AI-ML-Services" "Research Repos"

# Generate a report
python scripts/rename_branches.py --dry-run --report reports/rename-summary.md
```

### Issue Creation (Enhanced)

```bash
# Interactive mode
python scripts/create_issues.py ProjectName

# Create from template
python scripts/create_issues.py ProjectName --template epic \
  --vars "epic_name=User Authentication" \
  --vars "description=Implement OAuth2 login"

# Import from CSV
python scripts/create_issues.py ProjectName --import issues.csv

# List available templates
python scripts/create_issues.py --list-templates
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

## Configuration

The tools use a hierarchical configuration system:

1. **config/config.yaml** - Default configuration
2. **Environment variables** - Override config values
3. **Command line arguments** - Override everything

Example configuration:

```yaml
gitlab:
  rate_limit: 3
  timeout: 30
  
features:
  dry_run: false
  show_progress: true
  
branch_operations:
  skip_protected: true
  update_merge_requests: true
  
groups:
  - name: "AI-ML-Services"
    filters:
      exclude_archived: true
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