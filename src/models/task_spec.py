"""Task specification models for NLP-based issue creation."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .issue import IssueType, IssuePriority


class TaskSize(str, Enum):
    """Task size/effort estimation."""
    SMALL = "small"      # 1-2 hours
    MEDIUM = "medium"    # 2-8 hours
    LARGE = "large"      # 1-3 days
    XLARGE = "xlarge"    # 3+ days


class TaskCategory(str, Enum):
    """Task categories for better organization."""
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    DESIGN = "design"
    INFRASTRUCTURE = "infrastructure"
    BUGFIX = "bugfix"
    REFACTORING = "refactoring"


@dataclass
class TaskSpec:
    """Specification for a task extracted from natural language."""
    
    title: str
    description: str
    task_type: IssueType = IssueType.TASK
    priority: IssuePriority = IssuePriority.MEDIUM
    category: TaskCategory = TaskCategory.IMPLEMENTATION
    size: TaskSize = TaskSize.MEDIUM
    
    # Dependencies and relationships
    dependencies: List[str] = field(default_factory=list)  # Task titles this depends on
    blocks: List[str] = field(default_factory=list)  # Tasks that depend on this
    parent_task: Optional[str] = None  # For subtasks
    
    # Task metadata
    labels: List[str] = field(default_factory=list)
    assignee_hint: Optional[str] = None  # Extracted from description
    milestone_hint: Optional[str] = None  # Suggested milestone
    due_date_hint: Optional[str] = None  # Extracted deadline
    
    # Technical details
    technologies: List[str] = field(default_factory=list)  # Detected technologies
    components: List[str] = field(default_factory=list)  # System components affected
    
    # Confidence and source
    confidence_score: float = 1.0  # How confident we are about this task
    source_text: Optional[str] = None  # Original text this was extracted from
    extraction_method: str = "pattern"  # pattern, ai, manual
    
    def to_issue_data(self) -> Dict[str, Any]:
        """Convert to issue creation data."""
        # Build description with metadata
        description_parts = [self.description]
        
        if self.dependencies:
            description_parts.append("\n## Dependencies")
            for dep in self.dependencies:
                description_parts.append(f"- [ ] {dep}")
        
        if self.technologies:
            description_parts.append(f"\n## Technologies\n{', '.join(self.technologies)}")
        
        if self.components:
            description_parts.append(f"\n## Components\n{', '.join(self.components)}")
        
        if self.source_text:
            description_parts.append(f"\n## Extracted from\n> {self.source_text}")
        
        # Combine labels
        all_labels = list(set(self.labels + [
            self.task_type.value,
            self.category.value,
            f"size:{self.size.value}",
            f"priority:{self.priority.value}"
        ]))
        
        issue_data = {
            'title': self.title,
            'description': '\n'.join(description_parts),
            'labels': all_labels,
            'issue_type': self.task_type,
        }
        
        # Add weight based on size
        weight_map = {
            TaskSize.SMALL: 1,
            TaskSize.MEDIUM: 3,
            TaskSize.LARGE: 8,
            TaskSize.XLARGE: 13
        }
        issue_data['weight'] = weight_map.get(self.size, 3)
        
        return issue_data


@dataclass
class ProcessingResult:
    """Result of processing natural language description."""
    
    original_description: str
    extracted_tasks: List[TaskSpec]
    created_issues: List[Dict[str, Any]]
    processing_metadata: Dict[str, Any]
    
    # Timing information
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Summary statistics
    total_tasks: int = 0
    tasks_created: int = 0
    tasks_failed: int = 0
    
    def __post_init__(self):
        """Calculate summary statistics."""
        self.total_tasks = len(self.extracted_tasks)
        if self.created_issues:
            self.tasks_created = len([i for i in self.created_issues if i.get('success')])
            self.tasks_failed = len([i for i in self.created_issues if not i.get('success')])
    
    def to_summary(self) -> str:
        """Generate a summary of the processing result."""
        duration = (self.completed_at - self.started_at).total_seconds() if self.completed_at else 0
        
        summary = f"""
# Task Extraction Summary

**Original Description Length**: {len(self.original_description)} characters
**Processing Time**: {duration:.2f} seconds
**Total Tasks Extracted**: {self.total_tasks}
**Tasks Created**: {self.tasks_created}
**Tasks Failed**: {self.tasks_failed}

## Extracted Tasks:
"""
        for i, task in enumerate(self.extracted_tasks, 1):
            summary += f"\n{i}. **{task.title}**"
            summary += f"\n   - Type: {task.task_type.value}"
            summary += f"\n   - Priority: {task.priority.value}"
            summary += f"\n   - Size: {task.size.value}"
            if task.dependencies:
                summary += f"\n   - Dependencies: {', '.join(task.dependencies)}"
        
        return summary


@dataclass
class AIAnalysis:
    """Result of AI analysis of natural language description."""
    
    # Main components
    summary: str  # AI-generated summary
    main_objective: str  # Primary goal
    sub_objectives: List[str]  # Secondary goals
    
    # Extracted entities
    mentioned_users: List[str] = field(default_factory=list)
    mentioned_deadlines: List[str] = field(default_factory=list)
    mentioned_technologies: List[str] = field(default_factory=list)
    mentioned_priorities: List[str] = field(default_factory=list)
    
    # Task breakdown suggestions
    suggested_tasks: List[Dict[str, Any]] = field(default_factory=list)
    suggested_milestones: List[str] = field(default_factory=list)
    suggested_labels: List[str] = field(default_factory=list)
    
    # Risk and complexity assessment
    complexity_score: float = 0.5  # 0-1, where 1 is most complex
    risk_factors: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    
    # Metadata
    ai_model: str = "gpt-4"
    confidence_score: float = 0.0
    processing_time: float = 0.0