#!/usr/bin/env python3
"""
Debug script to identify issue parsing problems
"""

import os
import sys

def debug_issue_parsing(file_path):
    """Debug the issue parsing logic for a given file"""
    print(f"Debugging issue parsing for: {file_path}")
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File length: {len(content)} characters")
    
    # Split content by separator lines
    sections = content.split('________________________________________')
    print(f"Found {len(sections)} sections")
    
    # Process each section
    for i, section in enumerate(sections):
        print(f"\nSection {i+1}:")
        if not section.strip():
            print("  - Empty section, skipping")
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            print("  - No lines found, skipping")
            continue
        
        # Find the first line which should contain issue type and title
        first_line = lines[0].strip()
        print(f"  First line: '{first_line}'")
        
        # Check for Feature or Task
        if "[Feature]" in first_line:
            print("  - Found [Feature] tag")
            issue_type = "Feature"
            title = first_line.split("[Feature]")[1].strip()
            print(f"  - Title: '{title}'")
        elif "[Task]" in first_line:
            print("  - Found [Task] tag")
            issue_type = "Task"
            title = first_line.split("[Task]")[1].strip()
            print(f"  - Title: '{title}'")
        else:
            print("  ❌ Error: No [Feature] or [Task] tag found in first line")
            print("  - This section will be skipped by the parser")
            continue

        # Show the next few lines for context
        for j, line in enumerate(lines[1:4]):
            print(f"  Line {j+2}: '{line}'")


if __name__ == "__main__":
    # Use the file passed as argument or default to issues-ocr-validation.txt
    file_path = sys.argv[1] if len(sys.argv) > 1 else "issues/issues-ocr-validation.txt"
    debug_issue_parsing(file_path) 