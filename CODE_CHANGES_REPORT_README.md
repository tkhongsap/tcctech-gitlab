# Code Changes Report Generator

A comprehensive GitLab analytics tool that generates detailed reports showing code changes (lines added/removed) **by individual branches** across projects and groups over multiple time periods, with **full branch analysis** to capture all development activity.

## Features

- **Branch-Level Analysis**: Shows statistics for each active branch individually (not aggregated by project)
- **Multi-branch Analysis**: Analyzes commits from all active branches (not just main/master)
- **Multi-timeframe Analysis**: Shows code changes for 7, 15, 30, 60, and 90-day periods
- **Group Organization**: Groups results by GitLab groups with friendly names
- **Contributor Tracking**: Counts unique contributors per branch for each time period
- **Development Visibility**: See exactly which branches your team is working on
- **Smart Filtering**: Special filtering for iland group (only shows llama-index projects)
- **Rich Formatting**: Beautiful table output with color coding and progress indicators
- **HTML Reports**: Generate stunning HTML reports in shadcn/ui style with responsive design
- **Export Options**: Save reports to text files or HTML for sharing and presentations
- **Performance Options**: Choose between comprehensive analysis or faster default-branch-only mode

## Key Improvements Over Default Branch Analysis

The script now analyzes **all active branches** by default, which means it captures:
- Feature branch development
- Hotfix branches
- Development/staging branches
- Any other active branches with recent commits

This provides a much more accurate picture of actual development activity compared to only looking at the main branch.

## Output Format

The report includes these columns:
- **Group**: GitLab group name (AI-ML-Services, Research Repos, etc.)
- **Project**: Project name
- **Branch**: Individual branch name (main, develop, feature/api, etc.)
- **Contributors (90d)**: Number of unique contributors to this branch in the last 90 days
- **7/15/30/60/90 days**: Code changes in format "+1,234 -567 (net: +667)"

### Branch-Level Reporting
Each row represents a specific branch within a project, allowing you to see:
- Which branches are actively being worked on
- How development effort is distributed across branches
- Whether projects are well-organized (good branch management)
- Team workflow patterns (main vs feature branches)

### Data Sorting
Results are automatically sorted by:
1. **Group** (alphabetical A-Z, case-insensitive)
2. **Project** (alphabetical A-Z, case-insensitive)
3. **7-day code changes** (highest activity first within each project)

This groups projects together while showing the most active branches first within each project, providing clear visibility into productivity by group and project.

## Group Mappings

- **1721**: AI-ML-Services
- **1267**: Research Repos  
- **1269**: Internal Services
- **119**: iland (filtered to show only llama-index projects)

## Usage

### Basic Usage
```bash
# Analyze all groups with full branch analysis (recommended)
python scripts/generate_code_changes_report.py

# Analyze specific groups
python scripts/generate_code_changes_report.py --groups 1721,1267,1269

# Save to text file
python scripts/generate_code_changes_report.py --output code_changes_report.txt

# Generate beautiful HTML report (shadcn/ui style)
python scripts/generate_code_changes_report.py --html report.html
```

### Performance Options
```bash
# Faster analysis (default branch only) - may miss feature branch activity
python scripts/generate_code_changes_report.py --default-branch-only

# Full analysis with all active branches (default behavior)
python scripts/generate_code_changes_report.py
```

## Sample Output

```
📊 CODE CHANGES REPORT BY GROUP, PROJECT, AND BRANCH
================================================================================
Group           Project              Branch          Contributors 7 Days               15 Days              30 Days              60 Days              90 Days              
--------------------------------------------------------------------------------
AI-ML-Services  llama-index-rag-...  main            2            +1,234 -567 (net: +667) +2,345 -890 (net: +1,455) +3,456 -1,234 (net: +2,222) +4,567 -1,567 (net: +3,000) +5,678 -2,000 (net: +3,678)
AI-ML-Services  llama-index-rag-...  develop         1            +456 -123 (net: +333)   +789 -234 (net: +555)     +1,234 -345 (net: +889)     +1,678 -456 (net: +1,222) +2,345 -678 (net: +1,667)
AI-ML-Services  dts-code-buddy       feature/ai      1            +890 -234 (net: +656)   +1,456 -456 (net: +1,000) +2,234 -678 (net: +1,556) +3,345 -890 (net: +2,455) +4,456 -1,123 (net: +3,333)
AI-ML-Services  dts-code-buddy       main            1            +234 -89 (net: +145)    +456 -123 (net: +333)     +678 -234 (net: +444)     +890 -345 (net: +545)   +1,123 -456 (net: +667)

Research Repos  fine-tune-vision     main            1            +456 -123 (net: +333)   +789 -234 (net: +555)     +1,234 -345 (net: +889)     +1,678 -456 (net: +1,222) +2,345 -678 (net: +1,667)

📈 SUMMARY STATISTICS
   Total Branches Analyzed: 25
   Unique Projects: 15
   Active Branches (7d): 12
   Active Branches (30d): 18
   Active Branches (90d): 22
   Total Lines Added (90d): 45,678
   Total Lines Deleted (90d): 12,345
   Net Code Change (90d): +33,333
```

## Requirements

- Python 3.7+
- GitLab API access (GITLAB_URL and GITLAB_TOKEN environment variables)
- Optional: `rich` library for enhanced table formatting (`pip install rich`)

## Environment Setup

Create a `.env` file in your project root:
```
GITLAB_URL=https://your-gitlab-instance.com
GITLAB_TOKEN=your-gitlab-api-token
```

## Technical Details

### Branch Discovery Process
1. **Get All Branches**: Retrieves all branches for each project
2. **Filter Active Branches**: Identifies branches with commits in the specified time period
3. **Collect Statistics**: Gathers commit stats from all active branches
4. **Deduplicate Commits**: Ensures commits appearing in multiple branches are only counted once
5. **Aggregate Results**: Combines statistics across all active branches

### Special Filtering
- **iland Group (119)**: Only analyzes projects containing "llama-index" in the name
- **Error Handling**: Gracefully handles branch access errors and continues analysis
- **Performance**: Optimized to minimize API calls while providing comprehensive coverage

### Performance Comparison
- **Default Branch Only**: ~2-3 API calls per project (faster)
- **All Active Branches**: ~5-15 API calls per project (comprehensive)

Choose the mode based on your needs:
- Use default behavior for comprehensive analysis
- Use `--default-branch-only` for quick checks or when all work happens on main branch

## Command Line Options

- `--groups`, `-g`: **Optional** - Comma-separated list of GitLab group IDs to analyze (default: all known groups)
- `--all-groups`: **Optional** - Analyze all known groups (same as default behavior)  
- `--output`, `-o`: **Optional** - Output file path for text report (prints to console if not specified)
- `--html`: **Optional** - Generate HTML report file (e.g., `--html report.html`)
- `--default-branch-only`: **Optional** - Only analyze default branch (faster, but may miss feature branch activity)

## Sample Output

```
📊 CODE CHANGES REPORT BY GROUP AND PROJECT
=====================================================================================================
Group           Project              Contributors 7 Days               15 Days              30 Days              60 Days              90 Days             
-----------------------------------------------------------------------------------------------------
AI-ML-Services  llama-index-rag...   4            +1,234 -567 (net: +667) +2,345 -1,234 (net: +1,111) +3,456 -1,890 (net: +1,566) +5,678 -2,345 (net: +3,333) +7,890 -3,456 (net: +4,434)
AI-ML-Services  dts-code-buddy       3            +456 -234 (net: +222)   +789 -345 (net: +444)     +1,123 -456 (net: +667)   +1,456 -678 (net: +778)   +1,789 -890 (net: +899) 
                    
Research Repos  fine-tune-vision     2            +123 -45 (net: +78)     +234 -89 (net: +145)      +345 -123 (net: +222)     +456 -234 (net: +222)     +567 -345 (net: +222)
Research Repos  label-studio         1            No changes               +45 -12 (net: +33)        +67 -23 (net: +44)        +89 -34 (net: +55)        +111 -45 (net: +66)
```

## Group IDs Reference

The script includes predefined group names for common groups:
- `1721`: AI-ML-Services
- `1267`: Research Repos
- `1269`: Internal Services  
- `119`: iland

## How It Works

1. **Fetches Projects**: Gets all active (non-archived) projects from specified groups
2. **Analyzes Commits**: For each project, retrieves commits for the last 7, 15, and 30 days
3. **Calculates Statistics**: Extracts line additions/deletions and contributor counts
4. **Formats Results**: Displays data in a readable table format, grouped by GitLab groups
5. **Provides Summary**: Shows aggregate statistics at the end

## Error Handling

- Handles API rate limits and network errors gracefully
- Continues processing other projects if one fails
- Shows clear error messages for missing configuration
- Includes fallback formatting if Rich library is not available

## Examples

### Analyze specific groups
```bash
python scripts/generate_code_changes_report.py --groups 1721,1267
```

### Get help
```bash
python scripts/generate_code_changes_report.py --help
```

## Output Explanation

- **+XXX -YYY (net: +/-ZZZ)**: XXX lines added, YYY lines deleted, ZZZ net change
- **Contributors**: Number of unique contributors in the specified time period
- **No changes**: No commits found in the time period

## Notes

- The script uses GitLab's commit statistics API to get accurate line counts
- Only active (non-archived) projects are included
- Time periods are calculated from the current date/time
- Projects are sorted by total activity (90-day period) within each group
- Contributors count shown is for the 90-day period for better overall view 