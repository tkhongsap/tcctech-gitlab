"""Tests for NLP issue service."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.nlp_issue_service import NLPIssueService
from src.models import IssueType, IssuePriority
from src.models.task_spec import TaskSpec, TaskSize, TaskCategory, AIAnalysis


class TestNLPIssueService:
    """Test NLP issue service functionality."""
    
    @pytest.fixture
    def mock_gitlab_client(self):
        """Create mock GitLab client."""
        return Mock()
    
    @pytest.fixture
    def nlp_service(self, mock_gitlab_client):
        """Create NLP service instance."""
        return NLPIssueService(mock_gitlab_client)
    
    def test_pattern_analysis(self, nlp_service):
        """Test pattern-based analysis."""
        description = """
        We need to implement user authentication with OAuth support.
        This is a critical feature that should be done ASAP.
        The implementation should use Python and FastAPI.
        After authentication is done, we need to add user profile management.
        """
        
        analysis = nlp_service._analyze_with_patterns(description)
        
        # Check task indicators found
        assert len(analysis['task_indicators']) > 0
        assert any('user authentication' in ind['text'] for ind in analysis['task_indicators'])
        
        # Check priority detection
        assert IssuePriority.CRITICAL in analysis['priorities']
        
        # Check technology detection
        assert 'python' in analysis['technologies']
        assert 'fastapi' in analysis['technologies']
        
        # Check dependency detection
        assert any('authentication' in dep for dep in analysis['dependencies'])
    
    def test_task_extraction_simple(self, nlp_service):
        """Test simple task extraction."""
        description = "We need to fix the login bug and add password reset functionality."
        
        analysis = nlp_service._analyze_with_patterns(description)
        tasks = nlp_service._extract_tasks_from_patterns(description, analysis)
        
        assert len(tasks) >= 2
        
        # Check first task
        bug_task = next((t for t in tasks if 'login bug' in t.title.lower()), None)
        assert bug_task is not None
        assert bug_task.task_type == IssueType.BUG
        assert bug_task.category == TaskCategory.BUGFIX
    
    def test_task_extraction_with_details(self, nlp_service):
        """Test task extraction with detailed information."""
        description = """
        Urgent: We need to implement the following features by end of month:
        
        1. User authentication with JWT tokens - this is critical
        2. REST API endpoints for CRUD operations (small task)
        3. Add comprehensive documentation for the API
        4. Research and implement caching with Redis
        
        The authentication depends on having the database schema ready.
        All tasks should be done using Python and FastAPI.
        """
        
        analysis = nlp_service._analyze_with_patterns(description)
        tasks = nlp_service._extract_tasks_from_patterns(description, analysis)
        
        # Should extract at least 4 tasks
        assert len(tasks) >= 4
        
        # Check authentication task
        auth_task = next((t for t in tasks if 'authentication' in t.title.lower()), None)
        assert auth_task is not None
        assert auth_task.priority == IssuePriority.CRITICAL
        assert 'jwt' in auth_task.title.lower() or 'jwt' in auth_task.description.lower()
        
        # Check documentation task
        doc_task = next((t for t in tasks if 'documentation' in t.title.lower()), None)
        assert doc_task is not None
        assert doc_task.task_type == IssueType.DOCUMENTATION
        
        # Check research task
        research_task = next((t for t in tasks if 'research' in t.title.lower()), None)
        assert research_task is not None
        assert research_task.task_type == IssueType.RESEARCH
        
        # Check technologies are captured
        for task in tasks:
            assert 'python' in task.technologies
            assert 'fastapi' in task.technologies
    
    def test_priority_detection(self, nlp_service):
        """Test priority detection from text."""
        test_cases = [
            ("This is a critical bug that needs immediate attention", IssuePriority.CRITICAL),
            ("High priority: implement user authentication", IssuePriority.HIGH),
            ("Nice to have: add dark mode support", IssuePriority.LOW),
            ("Add new feature", IssuePriority.MEDIUM),  # Default
        ]
        
        for description, expected_priority in test_cases:
            analysis = nlp_service._analyze_with_patterns(description)
            tasks = nlp_service._extract_tasks_from_patterns(description, analysis)
            
            assert len(tasks) > 0
            assert tasks[0].priority == expected_priority
    
    def test_size_estimation(self, nlp_service):
        """Test task size estimation."""
        test_cases = [
            ("Quick fix: update the button color", TaskSize.SMALL),
            ("Large refactoring of the authentication module", TaskSize.LARGE),
            ("Epic: Complete redesign of the user interface", TaskSize.XLARGE),
            ("Implement new API endpoint", TaskSize.MEDIUM),  # Default
        ]
        
        for description, expected_size in test_cases:
            analysis = nlp_service._analyze_with_patterns(description)
            tasks = nlp_service._extract_tasks_from_patterns(description, analysis)
            
            assert len(tasks) > 0
            assert tasks[0].size == expected_size
    
    def test_dependency_extraction(self, nlp_service):
        """Test dependency extraction."""
        description = """
        First, we need to set up the database schema.
        After completing the database setup, implement the user model.
        Once the user model is done, add authentication endpoints.
        The frontend depends on the authentication endpoints being ready.
        """
        
        analysis = nlp_service._analyze_with_patterns(description)
        tasks = nlp_service._extract_tasks_from_patterns(description, analysis)
        
        # Find authentication task
        auth_task = next((t for t in tasks if 'authentication' in t.title.lower()), None)
        assert auth_task is not None
        assert len(auth_task.dependencies) > 0
    
    def test_technology_detection(self, nlp_service):
        """Test technology detection."""
        description = """
        Build a microservices architecture using:
        - Python with FastAPI for the main service
        - React for the frontend
        - PostgreSQL for the database
        - Docker and Kubernetes for deployment
        - GitLab CI/CD for automation
        """
        
        analysis = nlp_service._analyze_with_patterns(description)
        
        expected_techs = ['python', 'fastapi', 'react', 'postgresql', 'docker', 'kubernetes', 'gitlab']
        for tech in expected_techs:
            assert tech in [t.lower() for t in analysis['technologies']]
    
    def test_generate_title(self, nlp_service):
        """Test title generation."""
        test_cases = [
            ("We need to implement user authentication", "Implement user authentication"),
            ("Must fix the critical login bug", "Fix the critical login bug"),
            ("Should add logging to all API endpoints", "Add logging to all API endpoints"),
            ("Create comprehensive test suite for the authentication module with 100% coverage", 
             "Create comprehensive test suite for the authentication module with 100%..."),
        ]
        
        for text, expected_title in test_cases:
            title = nlp_service._generate_title(text)
            assert title == expected_title
    
    @patch('src.services.nlp_issue_service.IssueService.create_issue')
    def test_process_description_dry_run(self, mock_create_issue, nlp_service):
        """Test processing description in dry run mode."""
        description = "Fix the login bug and add user registration"
        
        result = nlp_service.process_description(
            project_id="123",
            description=description,
            dry_run=True
        )
        
        # Should not create any issues in dry run
        mock_create_issue.assert_not_called()
        
        # Should extract tasks
        assert len(result.extracted_tasks) > 0
        assert result.total_tasks == len(result.extracted_tasks)
        
        # Should have preview results
        assert all(r.get('preview') for r in result.created_issues)
    
    @patch('src.services.nlp_issue_service.IssueService.create_issue')
    def test_process_description_create(self, mock_create_issue, nlp_service):
        """Test processing description with issue creation."""
        # Mock successful issue creation
        mock_issue = Mock()
        mock_issue.id = 1
        mock_issue.iid = 101
        mock_issue.title = "Test Issue"
        mock_issue.web_url = "https://gitlab.com/project/issues/101"
        mock_create_issue.return_value = mock_issue
        
        description = "Implement user authentication"
        
        result = nlp_service.process_description(
            project_id="123",
            description=description,
            dry_run=False
        )
        
        # Should create issues
        assert mock_create_issue.called
        assert result.tasks_created > 0
        assert result.tasks_failed == 0
    
    def test_sort_by_dependencies(self, nlp_service):
        """Test task sorting by dependencies."""
        # Create tasks with dependencies
        task1 = TaskSpec(title="Setup database", description="Setup database")
        task2 = TaskSpec(title="Create user model", description="Create user model", 
                        dependencies=["Setup database"])
        task3 = TaskSpec(title="Add authentication", description="Add authentication",
                        dependencies=["Create user model"])
        task4 = TaskSpec(title="Add frontend", description="Add frontend",
                        dependencies=["Add authentication"])
        
        # Test different orders
        tasks = [task4, task2, task3, task1]  # Wrong order
        sorted_tasks = nlp_service._sort_by_dependencies(tasks)
        
        # Check correct order
        assert sorted_tasks[0].title == "Setup database"
        assert sorted_tasks[1].title == "Create user model"
        assert sorted_tasks[2].title == "Add authentication"
        assert sorted_tasks[3].title == "Add frontend"
    
    def test_ai_integration(self, nlp_service):
        """Test AI integration."""
        # Create mock AI client
        mock_ai_client = Mock()
        mock_analysis = AIAnalysis(
            summary="Test project",
            main_objective="Build test system",
            suggested_tasks=[
                {
                    'title': 'Setup project structure',
                    'type': 'task',
                    'priority': 'high',
                    'size': 'small'
                }
            ]
        )
        mock_ai_client.analyze_description.return_value = mock_analysis
        
        # Create service with AI
        nlp_service_ai = NLPIssueService(nlp_service.gitlab, mock_ai_client)
        
        result = nlp_service_ai.process_description(
            project_id="123",
            description="Build a test system",
            use_ai=True,
            dry_run=True
        )
        
        # Should use AI
        mock_ai_client.analyze_description.assert_called_once()
        assert len(result.extracted_tasks) > 0
        assert result.extracted_tasks[0].extraction_method == 'ai'
    
    def test_enhance_with_context(self, nlp_service):
        """Test task enhancement with project context."""
        tasks = [
            TaskSpec(title="Fix authentication bug", description="Fix bug", 
                    technologies=['python'])
        ]
        
        context = {
            'existing_issues': [
                {'iid': 100, 'title': 'Fix authentication issue'},
                {'iid': 101, 'title': 'Add user management'}
            ],
            'team_members': [
                {'username': 'john', 'name': 'John Python Developer'},
                {'username': 'jane', 'name': 'Jane Smith'}
            ],
            'milestones': [
                {'title': 'v1.0', 'state': 'active'}
            ]
        }
        
        enhanced_tasks = nlp_service._enhance_with_context(tasks, "123", context)
        
        # Should find related issue
        assert "Related Issue" in enhanced_tasks[0].description
        assert "#100" in enhanced_tasks[0].description
        
        # Should suggest assignee based on technology match
        assert enhanced_tasks[0].assignee_hint == 'john'
        
        # Should suggest milestone
        assert enhanced_tasks[0].milestone_hint == 'v1.0'
    
    def test_empty_description(self, nlp_service):
        """Test handling of empty description."""
        result = nlp_service.process_description(
            project_id="123",
            description="",
            dry_run=True
        )
        
        # Should handle gracefully
        assert result.total_tasks == 0
        assert len(result.extracted_tasks) == 0
    
    def test_very_long_description(self, nlp_service):
        """Test handling of very long description."""
        # Create a long description with multiple tasks
        tasks_text = []
        for i in range(20):
            tasks_text.append(f"Task {i}: Implement feature {i} with proper testing and documentation")
        
        description = "\n".join(tasks_text)
        
        result = nlp_service.process_description(
            project_id="123",
            description=description,
            dry_run=True
        )
        
        # Should extract multiple tasks
        assert result.total_tasks > 10
        
        # Tasks should have reasonable titles
        for task in result.extracted_tasks:
            assert len(task.title) <= 80  # Title length limit