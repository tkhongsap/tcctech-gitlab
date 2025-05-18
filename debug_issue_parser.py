#!/usr/bin/env python3
"""
Debug Issue Parser

This script helps debug issues with the issue parser from 03_create_gitlab_issues.py.
"""

import os
import sys
from typing import Dict, List, Any
from dotenv import load_dotenv

# Import the parsing function from the main script
from 03_create_gitlab_issues import parse_issues_from_file, parse_issues_from_text


def debug_parse_issues_from_file(file_path: str, verbose: bool = True) -> None:
    """
    Debug the parsing of issues from a file with verbose output.
    
    Args:
        file_path: Path to the issue file
        verbose: Whether to print verbose debug info
    """
    print(f"Debugging parser for file: {file_path}")
    print("=" * 80)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"File content length: {len(content)} characters")
        print(f"First 100 characters: {content[:100]}...")
        
        if verbose:
            print("\nFull file content:")
            print("-" * 80)
            print(content)
            print("-" * 80)
        
        # Split content by separator lines to see sections
        sections = content.split('________________________________________')
        print(f"\nFound {len(sections)} sections separated by underscores")
        
        for i, section in enumerate(sections, 1):
            if not section.strip():
                print(f"  Section {i}: [Empty section]")
                continue
                
            lines = section.strip().split('\n')
            print(f"  Section {i}: {len(lines)} lines, starts with: {lines[0][:50]}...")
        
        # Try parsing the content
        print("\nAttempting to parse issues...")
        issues = parse_issues_from_text(content)
        
        print(f"Parsing complete. Found {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  Issue {i}: [{issue.get('type', 'Unknown')}] {issue.get('title', 'No Title')}")
            print(f"    Labels: {', '.join(issue.get('labels', []))}")
            print(f"    Description length: {len(issue.get('raw_description', ''))}")
            print(f"    Acceptance length: {len(issue.get('raw_acceptance', ''))}")
        
        if not issues:
            print("WARNING: No issues were parsed from the file!")
            print("This could indicate a format mismatch or parser issue.")
        
    except Exception as e:
        print(f"Error during debugging: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def main() -> None:
    """Main function to run the debug script."""
    if len(sys.argv) < 2:
        print("Usage: python debug_issue_parser.py <issue_file_path>")
        print("Example: python debug_issue_parser.py issues/issues_services_status.txt")
        sys.exit(1)
    
    issue_file = sys.argv[1]
    
    if not os.path.exists(issue_file):
        print(f"Error: File '{issue_file}' not found.")
        sys.exit(1)
    
    debug_parse_issues_from_file(issue_file)


if __name__ == "__main__":
    main() 