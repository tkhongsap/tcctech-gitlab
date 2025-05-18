# GitLab Tools

A collection of Python scripts for automating GitLab operations.

## Scripts

1. **01_gitlab_info_extractor.py** - Extracts information about groups, subgroups, and projects from a GitLab instance.
2. **02_gitlab_rename_trunk_to_main.py** - Renames 'trunk' branch to 'main' across multiple projects in a group.
3. **03_create_gitlab_issues.py** - Creates issues in a GitLab project based on a structured text file.

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

### Extract GitLab Information

```bash
python 01_gitlab_info_extractor.py
```

This script extracts information about a specific GitLab group and its subgroups, including:
- Group details
- Subgroup details
- Project/repository details
- Branch information
- Last commit details for each branch

The script outputs information to:
- Console (for interactive use)
- JSON file (for programmatic use)
- Markdown file (for documentation)
- CSV file (for spreadsheet applications)

### Rename Trunk to Main

```bash
python 02_gitlab_rename_trunk_to_main.py
```

This script automates renaming the 'trunk' branch to 'main' across all projects in a specific GitLab group:
- Checks if 'trunk' branch exists
- Creates 'main' branch from 'trunk'
- Updates default branch setting
- Deletes 'trunk' branch

### Create GitLab Issues

```bash
python 03_create_gitlab_issues.py [project_name] [issues_file]
```

This script creates issues in a GitLab project based on a structured text file:
- Arguments:
  - `project_name`: Name of the GitLab project (default: "Flow-RAG")
  - `issues_file`: Path to the file containing issue descriptions (default: "issues-flow-rag.txt")

- The issues file should follow a specific format:
  ```
  • [Feature/Task] Title
  o Description: 
      - Item 1
      - Item 2
  o Acceptance Criteria: 
      - Criterion 1
      - Criterion 2
  o Labels: label1, label2, label3
  ```

## Example Issues File

See `issues-flow-rag.txt` for an example of the structure expected by the issue creator script.

## Requirements

- Python 3.6 or higher
- Required packages:
  - requests
  - python-dotenv
  - typing

## License

This project is licensed under the MIT License - see the LICENSE file for details. 