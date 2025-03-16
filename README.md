# GitLab Information Extractor

This project contains a Python script to extract detailed information from an internal GitLab instance using the GitLab API.

## Overview

The `gitlab_info_extractor.py` script fetches information about a specific GitLab group and its subgroups. It displays details such as:
- Group names, IDs, paths, descriptions, visibility, and web URLs
- Projects within each group and subgroup
- All branches for each project
- Latest update information for each branch (commit date, author, and commit message)
- Summary information for each repository

## Repository Summary

For each repository, the script generates a summary that includes:
1. The total number of branches in the repository
2. The latest update on the main/trunk branch (date, author, and commit message)
3. The total number of developers that have contributed to the repository

## Prerequisites

- Python 3.6 or higher
- GitLab Personal Access Token (PAT) with appropriate permissions

## Installation

1. Clone the repository.
2. Navigate to the project directory and install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root with the following content:

```dotenv
GITLAB_URL=https://git.lab.tcctech.app
GITLAB_API_TOKEN=your_gitlab_token_here
```

> **Note:** Do not share your API token publicly. The token provided here is used for demonstration, and you should use your own secure token.

The `.gitignore` file is configured to prevent accidental commits of sensitive files like `.env`.

## Usage

Run the script using the following command:

```bash
python gitlab_info_extractor.py
```

The script will:
1. Output information to the console
2. Generate a JSON file with all extracted data
3. Generate a Markdown file with formatted information
4. Generate a CSV file with branch information across all repositories

### Output Files

The script generates three output files:
- `gitlab_info_ds_and_ml_research_sandbox.json` - Contains all data in JSON format
- `gitlab_info_ds_and_ml_research_sandbox.md` - Contains formatted information in Markdown
- `gitlab_info_ds_and_ml_research_sandbox.csv` - Contains branch data in CSV format

### Console Output

The script will output a hierarchical display of information to the console, including:

1. **Parent Group Information**
   - Details for "DS and ML Research Sandbox"

2. **Subgroups**
   - Details for each subgroup (Packages, Internal Services, Development (POC), Research Repos)
   
3. **Project Summary and Details**
   - Name, ID, Path, Description, Default Branch, and Web URL for each project
   - Repository summary showing:
     - Total number of branches
     - Latest update on main/trunk branch (date and author)
     - Number of contributors to the repository
   
4. **Branches for Each Project**
   - Branch names
   - When each branch was last updated (date and time)
   - Who updated each branch (author name)
   - The commit message for the last update

### JSON Format

The JSON output includes a comprehensive data structure with:
- Parent group information
- Subgroups and their details
- Projects within each group and subgroup
- Summary statistics for each repository
- Branches for each project with update information

This format is ideal for programmatic processing or integration with other tools.

### Markdown Format

The Markdown output provides a human-readable, formatted view of the information:
- Hierarchical headings for groups, subgroups, and projects
- Project summaries with branch counts, main branch updates, and contributor counts
- Tables for displaying branch information
- Hyperlinks to GitLab resources
- Formatted metadata

This format is ideal for documentation or sharing with team members.

### CSV Format

The CSV output provides a flat, tabular view of branch information across all repositories with the following columns:
1. **Group** - Top-level group name
2. **Subgroup** - Subgroup name (empty for projects directly in the parent group)
3. **Project/Repository** - Name of the repository
4. **Branch** - Name of the branch
5. **Updated By** - User who last updated the branch
6. **Last Updated** - Date and time of the last update
7. **Commit Message** - Message from the last commit

This format is ideal for:
- Importing into spreadsheet software (Excel, Google Sheets)
- Data analysis and filtering
- Creating reports and visualizations
- Sharing with non-technical team members

## Error Handling

- The script verifies the existence of required environment variables before proceeding.
- API requests are wrapped in `try-except` blocks. In case of network issues or API errors, appropriate error messages will be printed to the console.
- File operations have error handling to ensure the script doesn't crash.

## Customization

You can modify the group name to extract information from other groups on your GitLab instance by changing the `parent_group_name` variable in the `main()` function.

## License

This project is provided as-is for internal use. 