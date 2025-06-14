"""Natural Language Processing service for issue creation."""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from ..api import GitLabClient
from ..models import IssueCreate, IssueType, IssuePriority
from ..models.task_spec import TaskSpec, TaskSize, TaskCategory, ProcessingResult, AIAnalysis
from .issue_service import IssueService
from ..utils.logger import OperationLogger
from ..utils import ProgressTracker

logger = logging.getLogger(__name__)


class NLPIssueService:
    """Service for creating GitLab issues from natural language descriptions."""
    
    # Pattern definitions for task extraction
    TASK_PATTERNS = [
        # Action patterns
        r"(?:we\s+)?(?:need\s+to|should|must|have\s+to|want\s+to)\s+([^.]+)",
        r"(?:implement|create|build|develop|design|add|integrate)\s+([^.]+)",
        r"(?:fix|resolve|debug|troubleshoot|patch)\s+([^.]+)",
        r"(?:test|verify|validate|ensure)\s+([^.]+)",
        r"(?:document|write\s+docs?\s+for|explain)\s+([^.]+)",
        
        # List patterns
        r"[-•]\s*([^.\n]+)",
        r"\d+\.\s*([^.\n]+)",
        
        # Feature patterns
        r"(?:feature|functionality):\s*([^.\n]+)",
        r"(?:requirement|requirement\s+\d+):\s*([^.\n]+)",
    ]
    
    # Priority indicators
    PRIORITY_PATTERNS = {
        IssuePriority.CRITICAL: [
            r"critical", r"urgent", r"asap", r"immediately", r"blocker",
            r"show[\s-]?stopper", r"high[\s-]?priority", r"top[\s-]?priority"
        ],
        IssuePriority.HIGH: [
            r"important", r"high", r"priority", r"soon", r"quickly",
            r"as\s+soon\s+as\s+possible", r"next\s+sprint"
        ],
        IssuePriority.LOW: [
            r"low[\s-]?priority", r"nice[\s-]?to[\s-]?have", r"optional",
            r"when\s+possible", r"future", r"someday", r"backlog"
        ]
    }
    
    # Task type indicators
    TYPE_PATTERNS = {
        IssueType.BUG: [
            r"bug", r"fix", r"issue", r"problem", r"error", r"crash",
            r"broken", r"not\s+working", r"failure", r"defect"
        ],
        IssueType.FEATURE: [
            r"feature", r"new", r"implement", r"add", r"create",
            r"functionality", r"capability", r"enhancement"
        ],
        IssueType.DOCUMENTATION: [
            r"document", r"docs?", r"readme", r"guide", r"manual",
            r"instructions", r"wiki", r"api\s+docs?"
        ],
        IssueType.RESEARCH: [
            r"research", r"investigate", r"explore", r"study", r"analyze",
            r"evaluate", r"assess", r"proof[\s-]?of[\s-]?concept", r"poc"
        ]
    }
    
    # Size/effort indicators
    SIZE_PATTERNS = {
        TaskSize.SMALL: [
            r"small", r"quick", r"simple", r"easy", r"minor", r"trivial",
            r"few\s+hours?", r"1[\s-]?2\s+hours?"
        ],
        TaskSize.LARGE: [
            r"large", r"big", r"complex", r"major", r"significant",
            r"several\s+days?", r"week", r"sprint"
        ],
        TaskSize.XLARGE: [
            r"huge", r"massive", r"epic", r"multi[\s-]?sprint",
            r"month", r"quarter", r"long[\s-]?term"
        ]
    }
    
    # Technology patterns
    TECH_PATTERNS = [
        r"python", r"javascript", r"java", r"go", r"rust", r"ruby",
        r"react", r"vue", r"angular", r"django", r"flask", r"fastapi",
        r"docker", r"kubernetes", r"k8s", r"aws", r"azure", r"gcp",
        r"postgresql", r"mysql", r"mongodb", r"redis", r"elasticsearch",
        r"api", r"rest", r"graphql", r"grpc", r"websocket",
        r"oauth", r"jwt", r"auth(?:entication|orization)?",
        r"ci[\s/]?cd", r"gitlab[\s-]?ci", r"github[\s-]?actions"
    ]
    
    # Dependency patterns
    DEPENDENCY_PATTERNS = [
        r"after\s+(?:completing\s+)?([^,.\n]+)",
        r"depends?\s+on\s+([^,.\n]+)",
        r"requires?\s+([^,.\n]+)(?:\s+to\s+be\s+(?:done|completed))?",
        r"once\s+([^,.\n]+)\s+is\s+(?:done|completed|finished)",
        r"blocked\s+by\s+([^,.\n]+)"
    ]
    
    def __init__(self, gitlab_client: GitLabClient, ai_client: Optional[Any] = None):
        """Initialize NLP issue service.
        
        Args:
            gitlab_client: GitLab API client
            ai_client: Optional AI client for enhanced processing
        """
        self.gitlab = gitlab_client
        self.ai_client = ai_client
        self.base_service = IssueService(gitlab_client)
    
    def process_description(
        self,
        project_id: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        dry_run: bool = False,
        use_ai: bool = False
    ) -> ProcessingResult:
        """Process natural language description and create issues.
        
        Args:
            project_id: GitLab project ID or path
            description: Natural language description of tasks
            context: Optional context (existing issues, team info, etc.)
            dry_run: Preview without creating issues
            use_ai: Use AI for enhanced analysis
            
        Returns:
            ProcessingResult with extracted tasks and created issues
        """
        with OperationLogger(logger, "process NLP description", project_id=project_id):
            try:
                # Start processing
                result = ProcessingResult(
                    original_description=description,
                    extracted_tasks=[],
                    created_issues=[],
                    processing_metadata={}
                )
                
                # Analyze description
                if use_ai and self.ai_client:
                    analysis = self._analyze_with_ai(description, context)
                    result.processing_metadata['ai_analysis'] = analysis
                    tasks = self._extract_tasks_from_ai(analysis, description)
                else:
                    analysis = self._analyze_with_patterns(description)
                    result.processing_metadata['pattern_analysis'] = analysis
                    tasks = self._extract_tasks_from_patterns(description, analysis)
                
                # Enhance tasks with context
                if context:
                    tasks = self._enhance_with_context(tasks, project_id, context)
                
                # Sort tasks by dependencies
                tasks = self._sort_by_dependencies(tasks)
                
                result.extracted_tasks = tasks
                
                # Create issues if not dry run
                if not dry_run:
                    created_issues = self._create_issues(project_id, tasks)
                    result.created_issues = created_issues
                else:
                    # Preview mode
                    result.created_issues = [
                        {'success': True, 'preview': True, 'task': task}
                        for task in tasks
                    ]
                
                result.completed_at = datetime.now()
                
                logger.info(f"Processed description: {result.total_tasks} tasks extracted, "
                          f"{result.tasks_created} created, {result.tasks_failed} failed")
                
                return result
                
            except Exception as e:
                logger.error(f"Failed to process description: {e}")
                raise
    
    def _analyze_with_patterns(self, description: str) -> Dict[str, Any]:
        """Analyze description using pattern matching.
        
        Args:
            description: Natural language description
            
        Returns:
            Analysis results
        """
        analysis = {
            'task_indicators': [],
            'priorities': [],
            'types': [],
            'sizes': [],
            'technologies': [],
            'dependencies': [],
            'deadlines': []
        }
        
        # Normalize text
        text_lower = description.lower()
        
        # Find task indicators
        for pattern in self.TASK_PATTERNS:
            matches = re.finditer(pattern, description, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                analysis['task_indicators'].append({
                    'text': match.group(1) if match.groups() else match.group(0),
                    'pattern': pattern,
                    'position': match.span()
                })
        
        # Find priorities
        for priority, patterns in self.PRIORITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    analysis['priorities'].append(priority)
        
        # Find task types
        for task_type, patterns in self.TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    analysis['types'].append(task_type)
        
        # Find sizes
        for size, patterns in self.SIZE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    analysis['sizes'].append(size)
        
        # Find technologies
        for pattern in self.TECH_PATTERNS:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                analysis['technologies'].append(match.group(0))
        
        # Find dependencies
        for pattern in self.DEPENDENCY_PATTERNS:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                analysis['dependencies'].append(match.group(1))
        
        # Find deadlines
        deadline_patterns = [
            r"by\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"before\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"deadline[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"due\s+(?:date|by)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"by\s+(end\s+of\s+(?:week|month|quarter))",
            r"within\s+(\d+\s+(?:days?|weeks?|months?))"
        ]
        
        for pattern in deadline_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                analysis['deadlines'].append(match.group(1))
        
        return analysis
    
    def _extract_tasks_from_patterns(self, description: str, analysis: Dict[str, Any]) -> List[TaskSpec]:
        """Extract tasks from pattern analysis.
        
        Args:
            description: Original description
            analysis: Pattern analysis results
            
        Returns:
            List of extracted tasks
        """
        tasks = []
        seen_titles = set()
        
        # Extract tasks from indicators
        for indicator in analysis['task_indicators']:
            text = indicator['text'].strip()
            
            # Clean up the text
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.rstrip('.,;:')  # Remove trailing punctuation
            
            # Skip if too short or already seen
            if len(text) < 10 or text.lower() in seen_titles:
                continue
            
            seen_titles.add(text.lower())
            
            # Create task
            task = TaskSpec(
                title=self._generate_title(text),
                description=self._generate_description(text, description),
                source_text=text,
                extraction_method="pattern"
            )
            
            # Set priority
            if analysis['priorities']:
                task.priority = analysis['priorities'][0]  # Use highest priority found
            
            # Set type
            task_type = self._determine_task_type(text, analysis['types'])
            task.task_type = task_type
            
            # Set category
            task.category = self._determine_category(task_type, text)
            
            # Set size
            if analysis['sizes']:
                task.size = analysis['sizes'][0]
            
            # Add technologies
            task.technologies = list(set(analysis['technologies']))
            
            # Add labels
            task.labels = self._generate_labels(task)
            
            # Check for dependencies
            for dep in analysis['dependencies']:
                if dep.lower() in text.lower():
                    continue  # Skip self-references
                task.dependencies.append(self._generate_title(dep))
            
            tasks.append(task)
        
        # If no tasks found from patterns, try to create at least one from the description
        if not tasks and len(description) > 20:
            task = TaskSpec(
                title=self._generate_title(description[:100]),
                description=description,
                source_text=description,
                extraction_method="fallback",
                confidence_score=0.5
            )
            tasks.append(task)
        
        return tasks
    
    def _generate_title(self, text: str) -> str:
        """Generate a concise title from text.
        
        Args:
            text: Source text
            
        Returns:
            Generated title
        """
        # Remove common prefixes
        prefixes = [
            "we need to", "we should", "we must", "need to", "should", "must",
            "have to", "want to", "implement", "create", "build", "develop"
        ]
        
        title = text.lower()
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        # Limit length
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title
    
    def _generate_description(self, task_text: str, full_description: str) -> str:
        """Generate task description.
        
        Args:
            task_text: Extracted task text
            full_description: Full original description
            
        Returns:
            Generated description
        """
        description_parts = []
        
        # Add task text as main description
        description_parts.append(task_text)
        
        # Find relevant context from full description
        sentences = re.split(r'[.!?]+', full_description)
        relevant_sentences = []
        
        task_words = set(task_text.lower().split())
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            # If sentence shares significant words with task
            if len(task_words & sentence_words) >= 2 and sentence.strip() != task_text:
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            description_parts.append("\n## Context")
            for sentence in relevant_sentences[:3]:  # Limit to 3 sentences
                description_parts.append(f"- {sentence}")
        
        return '\n'.join(description_parts)
    
    def _determine_task_type(self, text: str, detected_types: List[IssueType]) -> IssueType:
        """Determine the most appropriate task type.
        
        Args:
            text: Task text
            detected_types: Types detected from patterns
            
        Returns:
            Most appropriate issue type
        """
        if detected_types:
            return detected_types[0]
        
        text_lower = text.lower()
        
        # Check for specific keywords
        if any(word in text_lower for word in ["bug", "fix", "error", "issue"]):
            return IssueType.BUG
        elif any(word in text_lower for word in ["document", "docs", "readme"]):
            return IssueType.DOCUMENTATION
        elif any(word in text_lower for word in ["research", "investigate", "explore"]):
            return IssueType.RESEARCH
        elif any(word in text_lower for word in ["feature", "add", "implement", "new"]):
            return IssueType.FEATURE
        
        return IssueType.TASK
    
    def _determine_category(self, task_type: IssueType, text: str) -> TaskCategory:
        """Determine task category based on type and text.
        
        Args:
            task_type: Issue type
            text: Task text
            
        Returns:
            Task category
        """
        text_lower = text.lower()
        
        if task_type == IssueType.BUG:
            return TaskCategory.BUGFIX
        elif task_type == IssueType.DOCUMENTATION:
            return TaskCategory.DOCUMENTATION
        elif task_type == IssueType.RESEARCH:
            return TaskCategory.RESEARCH
        elif "test" in text_lower or "verify" in text_lower:
            return TaskCategory.TESTING
        elif "design" in text_lower or "ui" in text_lower or "ux" in text_lower:
            return TaskCategory.DESIGN
        elif "deploy" in text_lower or "infrastructure" in text_lower:
            return TaskCategory.INFRASTRUCTURE
        elif "refactor" in text_lower or "clean" in text_lower:
            return TaskCategory.REFACTORING
        
        return TaskCategory.IMPLEMENTATION
    
    def _generate_labels(self, task: TaskSpec) -> List[str]:
        """Generate appropriate labels for a task.
        
        Args:
            task: Task specification
            
        Returns:
            List of labels
        """
        labels = []
        
        # Add type and category as labels
        labels.append(task.task_type.value)
        labels.append(task.category.value)
        
        # Add technology labels
        for tech in task.technologies:
            labels.append(f"tech:{tech}")
        
        # Add priority label if high or critical
        if task.priority in [IssuePriority.HIGH, IssuePriority.CRITICAL]:
            labels.append(f"priority:{task.priority.value}")
        
        # Add size label
        labels.append(f"size:{task.size.value}")
        
        return labels
    
    def _enhance_with_context(
        self,
        tasks: List[TaskSpec],
        project_id: str,
        context: Dict[str, Any]
    ) -> List[TaskSpec]:
        """Enhance tasks with project context.
        
        Args:
            tasks: List of tasks
            project_id: Project ID
            context: Project context
            
        Returns:
            Enhanced tasks
        """
        # Get existing issues if available
        existing_issues = context.get('existing_issues', [])
        team_members = context.get('team_members', [])
        milestones = context.get('milestones', [])
        
        for task in tasks:
            # Check for similar existing issues
            for issue in existing_issues:
                similarity = self._calculate_similarity(task.title, issue.get('title', ''))
                if similarity > 0.8:
                    task.description += f"\n\n## Related Issue\n- #{issue['iid']}: {issue['title']}"
            
            # Suggest assignee based on expertise
            if team_members and task.technologies:
                # This is a simple heuristic - could be enhanced
                for member in team_members:
                    member_name = member.get('name', '').lower()
                    for tech in task.technologies:
                        if tech in member_name or tech in member.get('bio', '').lower():
                            task.assignee_hint = member.get('username')
                            break
            
            # Suggest milestone
            if milestones:
                # Simple heuristic - assign to next open milestone
                open_milestones = [m for m in milestones if m.get('state') == 'active']
                if open_milestones:
                    task.milestone_hint = open_milestones[0].get('title')
        
        return tasks
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _sort_by_dependencies(self, tasks: List[TaskSpec]) -> List[TaskSpec]:
        """Sort tasks by dependencies.
        
        Args:
            tasks: List of tasks
            
        Returns:
            Sorted tasks
        """
        # Create a mapping of task titles
        task_map = {task.title: task for task in tasks}
        
        # Build dependency graph
        sorted_tasks = []
        visited = set()
        
        def visit(task: TaskSpec):
            if task.title in visited:
                return
            
            visited.add(task.title)
            
            # Visit dependencies first
            for dep_title in task.dependencies:
                if dep_title in task_map and dep_title not in visited:
                    visit(task_map[dep_title])
            
            sorted_tasks.append(task)
        
        # Visit all tasks
        for task in tasks:
            visit(task)
        
        return sorted_tasks
    
    def _create_issues(self, project_id: str, tasks: List[TaskSpec]) -> List[Dict[str, Any]]:
        """Create GitLab issues from tasks.
        
        Args:
            project_id: Project ID
            tasks: List of tasks
            
        Returns:
            List of creation results
        """
        results = []
        created_issues = {}  # Map task title to created issue
        
        progress = ProgressTracker(
            enumerate(tasks),
            total=len(tasks),
            description="Creating issues",
            unit="issues"
        )
        
        for i, task in progress:
            try:
                # Convert to issue data
                issue_data = task.to_issue_data()
                
                # Add dependencies as links if they were created
                if task.dependencies:
                    dep_links = []
                    for dep_title in task.dependencies:
                        if dep_title in created_issues:
                            dep_issue = created_issues[dep_title]
                            dep_links.append(f"- Depends on #{dep_issue['iid']}: {dep_issue['title']}")
                    
                    if dep_links:
                        issue_data['description'] += "\n\n## Dependencies\n" + '\n'.join(dep_links)
                
                # Create issue
                issue = self.base_service.create_issue(
                    project_id,
                    issue_data,
                    dry_run=False
                )
                
                if issue:
                    created_issues[task.title] = {
                        'id': issue.id,
                        'iid': issue.iid,
                        'title': issue.title,
                        'web_url': issue.web_url
                    }
                    
                    results.append({
                        'success': True,
                        'task': task,
                        'issue': issue,
                        'message': f"Created issue #{issue.iid}: {issue.title}"
                    })
                
            except Exception as e:
                logger.error(f"Failed to create issue for task '{task.title}': {e}")
                results.append({
                    'success': False,
                    'task': task,
                    'error': str(e),
                    'message': f"Failed to create issue: {e}"
                })
        
        return results
    
    def _analyze_with_ai(self, description: str, context: Optional[Dict[str, Any]]) -> AIAnalysis:
        """Analyze description using AI.
        
        Args:
            description: Natural language description
            context: Optional context
            
        Returns:
            AI analysis results
        """
        if not self.ai_client:
            raise ValueError("AI client not configured. Pass ai_client to constructor.")
        
        return self.ai_client.analyze_description(description, context)
    
    def _extract_tasks_from_ai(self, analysis: AIAnalysis, description: str) -> List[TaskSpec]:
        """Extract tasks from AI analysis.
        
        Args:
            analysis: AI analysis results
            description: Original description
            
        Returns:
            List of extracted tasks
        """
        # Import the helper function
        from .ai_service import extract_tasks_from_ai_analysis
        
        return extract_tasks_from_ai_analysis(analysis, description)