import os

def debug_parse_issues(file_path):
    print(f"Parsing file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Content read successfully. Length: {len(content)} chars.")
        
        # Skip the header line if present
        if content.startswith("High-Level GitLab Issues"):
            content = content.split('\n', 1)[1]
            print("Skipped header line.")

        # Split content by main numbered sections
        sections = []
        current_section = ""
        
        print("Splitting content into sections...")
        for line in content.split('\n'):
            if line.strip() and line[0].isdigit() and '. ' in line:
                print(f"Found section header: '{line}'")
                if current_section:
                    sections.append(current_section)
                    print(f"Added previous section: {len(current_section)} chars")
                current_section = line
            else:
                current_section += '\n' + line
        
        if current_section:
            sections.append(current_section)
            print(f"Added final section: {len(current_section)} chars")
        
        print(f"Total sections found: {len(sections)}")
        
        issues = []
        
        # Process each section
        for section_index, section in enumerate(sections):
            print(f"\nProcessing section {section_index + 1}:")
            lines = section.split('\n')
            if not lines:
                print("Empty section, skipping.")
                continue
            
            # Debug the first few lines of this section
            print(f"Section starts with: '{lines[0]}'")
            if len(lines) > 1:
                print(f"Second line: '{lines[1]}'")
            if len(lines) > 2:
                print(f"Third line: '{lines[2]}'")
            
            # Variables to accumulate issue data
            current_issue_title = ""
            current_issue_type = ""
            current_description = ""
            current_acceptance = ""
            current_labels = []
            
            # Flags to track what we're parsing
            parsing_feature = False
            parse_mode = None
            
            # Examine the first line for issue title and type
            first_line = lines[0].strip()
            if "[Feature]" in first_line:
                current_issue_type = "Feature"
                current_issue_title = first_line.split("[Feature]")[1].strip()
                parsing_feature = True
                print(f"Found Feature issue: '{current_issue_title}'")
            elif "[Task]" in first_line:
                current_issue_type = "Task"
                current_issue_title = first_line.split("[Task]")[1].strip()
                parsing_feature = True
                print(f"Found Task issue: '{current_issue_title}'")
            
            # Process the rest of the lines
            for line_index, line in enumerate(lines[1:], 1):
                line = line.strip()
                if not line:
                    continue
                
                # Look for Description, Acceptance, and Labels sections
                if line == "Description:":
                    parse_mode = "description"
                    print("Found Description section")
                elif line == "Acceptance Criteria:" or line == "Acceptance:":
                    parse_mode = "acceptance"
                    print("Found Acceptance Criteria section")
                elif line.startswith("Labels:"):
                    labels_text = line.split("Labels:", 1)[1].strip()
                    current_labels = [label.strip() for label in labels_text.split(',')]
                    if current_issue_type:
                        current_labels.append(current_issue_type.lower())
                    print(f"Found Labels: {current_labels}")
                # Handle content lines
                elif parse_mode == "description" and line and not line.startswith("_"):
                    if line.startswith('•'):
                        line = line[1:].strip()
                    current_description += f"- {line}\n"
                elif parse_mode == "acceptance" and line and not line.startswith("_"):
                    if line.startswith('•'):
                        line = line[1:].strip()
                    current_acceptance += f"- {line}\n"
            
            # Create issue if we found one
            if current_issue_title:
                formatted_description = "## Description\n"
                if current_description.strip():
                    formatted_description += current_description
                else:
                    formatted_description += "- No description provided.\n"
                
                formatted_description += "\n## Acceptance Criteria\n"
                if current_acceptance.strip():
                    formatted_description += current_acceptance
                else:
                    formatted_description += "- No acceptance criteria provided.\n"
                
                issue = {
                    'title': current_issue_title,
                    'description': formatted_description,
                    'labels': current_labels,
                    'type': current_issue_type,
                    'raw_description': current_description,
                    'raw_acceptance': current_acceptance
                }
                
                issues.append(issue)
                print(f"Added issue: {current_issue_title}")
        
        print(f"\nTotal issues found: {len(issues)}")
        
        if issues:
            print("\nFirst issue details:")
            print(f"Title: {issues[0]['title']}")
            print(f"Type: {issues[0]['type']}")
            print(f"Labels: {issues[0]['labels']}")
            print("Description preview:")
            desc_lines = issues[0]['raw_description'].strip().split('\n')
            for line in desc_lines[:2]:
                print(f"  {line}")
            print("Acceptance Criteria preview:")
            acc_lines = issues[0]['raw_acceptance'].strip().split('\n')
            for line in acc_lines[:2]:
                print(f"  {line}")
        
        return issues
    
    except Exception as e:
        print(f"Error parsing issues: {e}")
        import traceback
        traceback.print_exc()
        return []

issue_file = "issues/issue-flow-product-recommendation.txt"
debug_parse_issues(issue_file) 