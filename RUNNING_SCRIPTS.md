# Running the Scripts

## Quick Start

Since the full Python environment with all dependencies is not set up, use the simplified version:

### 1. Test GitLab Connection
```bash
python3 test_connection.py
```

### 2. Run Branch Rename Script (Simplified Version)

**Dry run (preview changes):**
```bash
python3 rename_branches_simple.py --dry-run
```

**Run with specific groups:**
```bash
python3 rename_branches_simple.py --groups "AI-ML-Services" --dry-run
```

**Rename different branches:**
```bash
python3 rename_branches_simple.py --old-branch develop --new-branch main --dry-run
```

**Actually perform the rename (remove --dry-run):**
```bash
python3 rename_branches_simple.py --old-branch develop --new-branch main
```

## Available Options

- `--old-branch` or `-o`: Source branch name (default: trunk)
- `--new-branch` or `-n`: Target branch name (default: main)
- `--groups` or `-g`: Specific groups to process (default: reads from config/config.yaml)
- `--dry-run`: Preview mode - shows what would be done without making changes

## Configured Groups

From config/config.yaml:
- AI-ML-Services
- Research Repos

## Full Script Setup

To use the full-featured script (scripts/rename_branches.py), you need to install dependencies:

### Option 1: With sudo access
```bash
sudo apt-get update && sudo apt-get install -y python3-pip python3-dotenv python3-tqdm
pip3 install -r requirements.txt
```

### Option 2: Without sudo (using virtual environment)
```bash
# Install python3-venv first (requires sudo)
sudo apt-get install python3-venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python scripts/rename_branches.py --help
```

## Current Status

The simplified script (rename_branches_simple.py) provides core functionality:
- ✅ Connects to GitLab
- ✅ Reads configuration
- ✅ Processes multiple groups and projects
- ✅ Dry-run mode
- ✅ Branch protection detection
- ✅ Progress reporting
- ❌ Advanced logging (requires additional dependencies)
- ❌ Progress bars (requires tqdm)
- ❌ Advanced configuration management (requires python-dotenv)

The script found that most projects don't have a 'trunk' branch, which is why they were skipped. You may want to check what branches your projects actually use.