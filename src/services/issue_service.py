"""Issue management service."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Iterator
from datetime import datetime, date
import logging

from ..api import GitLabClient
from ..models import Issue, IssueCreate, IssueTemplate, IssueType
from ..utils.validators import IssueValidator, FileValidator, ValidationError
from ..utils.logger import OperationLogger
from ..utils import ProgressTracker


logger = logging.getLogger(__name__)


class IssueService:
    """Service for managing GitLab issues."""
    
    def __init__(self, client: GitLabClient):
        """Initialize issue service.
        
        Args:
            client: GitLab API client
        """
        self.client = client
        self.templates: Dict[str, IssueTemplate] = {}
        self._load_builtin_templates()
    
    def _load_builtin_templates(self):
        """Load built-in issue templates."""
        # Feature template
        self.templates['feature'] = IssueTemplate(
            name='feature',
            title_template='[Feature] {feature_name}',
            description_template='''## Description
{description}

## Acceptance Criteria
{acceptance_criteria}

## Technical Details
{technical_details}

## Related Issues
{related_issues}
''',
            default_labels=['feature', 'needs-review'],
            default_issue_type=IssueType.FEATURE,
            required_variables=['feature_name', 'description', 'acceptance_criteria'],
            optional_variables=['technical_details', 'related_issues']
        )
        
        # Bug template
        self.templates['bug'] = IssueTemplate(
            name='bug',
            title_template='[Bug] {bug_title}',
            description_template='''## Bug Description
{description}

## Steps to Reproduce
{steps_to_reproduce}

## Expected Behavior
{expected_behavior}

## Actual Behavior
{actual_behavior}

## Environment
- **GitLab Version**: {gitlab_version}
- **Browser**: {browser}
- **OS**: {os}

## Additional Context
{additional_context}
''',
            default_labels=['bug', 'needs-triage'],
            default_issue_type=IssueType.BUG,
            required_variables=['bug_title', 'description', 'steps_to_reproduce', 'expected_behavior', 'actual_behavior'],
            optional_variables=['gitlab_version', 'browser', 'os', 'additional_context']
        )
        
        # Task template
        self.templates['task'] = IssueTemplate(
            name='task',
            title_template='{task_name}',
            description_template='''## Task Description
{description}

## Subtasks
{subtasks}

## Definition of Done
{definition_of_done}

## Notes
{notes}
''',
            default_labels=['task'],
            default_issue_type=IssueType.TASK,
            required_variables=['task_name', 'description'],
            optional_variables=['subtasks', 'definition_of_done', 'notes']
        )
    
    def load_template_from_file(self, file_path: Union[str, Path]) -> IssueTemplate:
        """Load a custom template from file.
        
        Args:
            file_path: Path to template file (YAML)
            
        Returns:
            Loaded template
        """
        path = FileValidator.validate_file_exists(file_path)
        template = IssueTemplate.from_file(str(path))
        self.templates[template.name] = template
        logger.info(f"Loaded template '{template.name}' from {path}")
        return template
    
    def create_issue(
        self,
        project_id: Union[int, str],
        issue_data: Union[IssueCreate, Dict[str, Any]],
        template_name: Optional[str] = None,
        dry_run: bool = False
    ) -> Optional[Issue]:
        """Create a single issue.
        
        Args:
            project_id: Project ID or path
            issue_data: Issue data (IssueCreate or dict)
            template_name: Optional template to apply
            dry_run: Preview without creating
            
        Returns:
            Created issue or None if dry run
        """
        # Convert dict to IssueCreate if needed
        if isinstance(issue_data, dict):
            validated_data = IssueValidator.validate_issue_data(issue_data)
            issue_create = IssueCreate(**validated_data)
        else:
            issue_create = issue_data
        
        # Apply template if specified
        if template_name:
            if template_name not in self.templates:
                raise ValueError(f"Template '{template_name}' not found")
            template = self.templates[template_name]
            issue_create.apply_template(template)
        
        # Add timestamp if configured
        if hasattr(self, 'config') and self.config.get('issue_operations.add_timestamp', True):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if issue_create.description:
                issue_create.description += f"\n\n---\n_Created at: {timestamp}_"
            else:
                issue_create.description = f"_Created at: {timestamp}_"
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create issue: {issue_create.title}")
            return None
        
        with OperationLogger(logger, "create issue", project_id=project_id):
            try:
                response = self.client.create_issue(
                    project_id,
                    **issue_create.to_gitlab_params()
                )
                issue = Issue.from_gitlab_response(response)
                logger.info(f"Created issue #{issue.iid}: {issue.title}")
                return issue
            except Exception as e:
                logger.error(f"Failed to create issue: {e}")
                raise
    
    def create_issues_bulk(
        self,
        project_id: Union[int, str],
        issues_data: List[Union[IssueCreate, Dict[str, Any]]],
        template_name: Optional[str] = None,
        dry_run: bool = False,
        stop_on_error: bool = False
    ) -> Dict[str, Any]:
        """Create multiple issues in bulk.
        
        Args:
            project_id: Project ID or path
            issues_data: List of issue data
            template_name: Optional template to apply to all
            dry_run: Preview without creating
            stop_on_error: Stop if any issue fails
            
        Returns:
            Summary of operation
        """
        results = {
            'total': len(issues_data),
            'created': 0,
            'failed': 0,
            'errors': [],
            'issues': []
        }
        
        progress = ProgressTracker(
            enumerate(issues_data),
            total=len(issues_data),
            description="Creating issues",
            unit="issues"
        )
        
        for i, issue_data in progress:
            try:
                issue = self.create_issue(
                    project_id,
                    issue_data,
                    template_name,
                    dry_run
                )
                if issue:
                    results['created'] += 1
                    results['issues'].append(issue)
                elif dry_run:
                    results['created'] += 1
            except Exception as e:
                results['failed'] += 1
                error_msg = f"Issue {i+1}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
                
                if stop_on_error:
                    break
        
        return results
    
    def import_from_csv(
        self,
        project_id: Union[int, str],
        csv_file: Union[str, Path],
        template_name: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Import issues from CSV file.
        
        Expected CSV columns:
        - title (required)
        - description
        - labels (comma-separated)
        - due_date (YYYY-MM-DD)
        - weight
        - assignee_usernames (comma-separated)
        - milestone_title
        
        Args:
            project_id: Project ID or path
            csv_file: Path to CSV file
            template_name: Optional template to apply
            dry_run: Preview without creating
            
        Returns:
            Import summary
        """
        path = FileValidator.validate_file_exists(csv_file)
        FileValidator.validate_file_extension(path, ['.csv'])
        
        issues_data = []
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Convert CSV row to issue data
                    issue_data = {
                        'title': row.get('title', '').strip()
                    }
                    
                    if 'description' in row:
                        issue_data['description'] = row['description'].strip()
                    
                    if 'labels' in row and row['labels']:
                        issue_data['labels'] = [
                            label.strip() 
                            for label in row['labels'].split(',')
                            if label.strip()
                        ]
                    
                    if 'due_date' in row and row['due_date']:
                        issue_data['due_date'] = row['due_date'].strip()
                    
                    if 'weight' in row and row['weight']:
                        issue_data['weight'] = int(row['weight'])
                    
                    # Handle template variables
                    if template_name:
                        template_vars = {}
                        for key, value in row.items():
                            if key.startswith('var_'):
                                var_name = key[4:]  # Remove 'var_' prefix
                                template_vars[var_name] = value
                        if template_vars:
                            issue_data['template_variables'] = template_vars
                    
                    issues_data.append(issue_data)
                    
                except Exception as e:
                    logger.error(f"Error parsing CSV row {row_num}: {e}")
                    if not dry_run:
                        raise ValidationError(f"Invalid data in row {row_num}: {e}")
        
        logger.info(f"Parsed {len(issues_data)} issues from CSV")
        
        return self.create_issues_bulk(
            project_id,
            issues_data,
            template_name,
            dry_run
        )
    
    def import_from_json(
        self,
        project_id: Union[int, str],
        json_file: Union[str, Path],
        template_name: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Import issues from JSON file.
        
        Args:
            project_id: Project ID or path
            json_file: Path to JSON file
            template_name: Optional template to apply
            dry_run: Preview without creating
            
        Returns:
            Import summary
        """
        path = FileValidator.validate_file_exists(json_file)
        FileValidator.validate_file_extension(path, ['.json'])
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'issues' in data:
            issues_data = data['issues']
        elif isinstance(data, list):
            issues_data = data
        else:
            raise ValidationError(
                "Invalid JSON format. Expected list of issues or "
                "object with 'issues' key"
            )
        
        logger.info(f"Loaded {len(issues_data)} issues from JSON")
        
        return self.create_issues_bulk(
            project_id,
            issues_data,
            template_name,
            dry_run
        )
    
    def parse_text_format(self, content: str) -> List[Dict[str, Any]]:
        """Parse issues from the legacy text format.
        
        Args:
            content: Text content in legacy format
            
        Returns:
            List of parsed issue data
        """
        issues = []
        
        # Split by separator
        sections = content.split('_' * 40)
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.strip().split('\n')
            issue_data = {}
            
            # Parse title
            for line in lines:
                if '[Feature]' in line:
                    issue_data['title'] = line.split('[Feature]')[1].strip()
                    issue_data['labels'] = ['feature']
                    break
                elif '[Task]' in line:
                    issue_data['title'] = line.split('[Task]')[1].strip()
                    issue_data['labels'] = ['task']
                    break
                elif '[Bug]' in line:
                    issue_data['title'] = line.split('[Bug]')[1].strip()
                    issue_data['labels'] = ['bug']
                    break
            
            if 'title' not in issue_data:
                continue
            
            # Parse other fields
            description_parts = []
            
            for line in lines:
                if line.strip().startswith('Description:'):
                    desc = line.split('Description:', 1)[1].strip()
                    if desc:
                        description_parts.append(f"## Description\n{desc}")
                elif line.strip().startswith('Acceptance:') or line.strip().startswith('Acceptance Criteria:'):
                    acc = line.split(':', 1)[1].strip()
                    if acc:
                        description_parts.append(f"## Acceptance Criteria\n{acc}")
                elif line.strip().startswith('Labels:'):
                    labels = line.split('Labels:', 1)[1].strip()
                    if labels:
                        issue_data['labels'].extend([
                            label.strip() 
                            for label in labels.split(',')
                            if label.strip()
                        ])
            
            if description_parts:
                issue_data['description'] = '\n\n'.join(description_parts)
            
            issues.append(issue_data)
        
        return issues
    
    def get_project_milestones(
        self, 
        project_id: Union[int, str]
    ) -> List[Dict[str, Any]]:
        """Get available milestones for a project.
        
        Args:
            project_id: Project ID or path
            
        Returns:
            List of milestones
        """
        milestones = list(self.client._paginated_get(
            f'projects/{project_id}/milestones',
            state='active'
        ))
        return milestones
    
    def get_project_members(
        self, 
        project_id: Union[int, str]
    ) -> List[Dict[str, Any]]:
        """Get project members for assignee selection.
        
        Args:
            project_id: Project ID or path
            
        Returns:
            List of project members
        """
        members = list(self.client._paginated_get(
            f'projects/{project_id}/members'
        ))
        return members