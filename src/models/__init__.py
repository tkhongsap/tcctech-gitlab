"""Data models for GitLab entities."""

from .issue import Issue, IssueCreate, IssueTemplate, IssueType, IssuePriority
from .project import Project, ProjectCreate
from .branch import Branch, BranchOperation, BranchOperationType
from .task_spec import TaskSpec, TaskSize, TaskCategory, ProcessingResult, AIAnalysis

__all__ = [
    'Issue', 'IssueCreate', 'IssueTemplate', 'IssueType', 'IssuePriority',
    'Project', 'ProjectCreate',
    'Branch', 'BranchOperation', 'BranchOperationType',
    'TaskSpec', 'TaskSize', 'TaskCategory', 'ProcessingResult', 'AIAnalysis'
]