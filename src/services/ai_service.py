"""AI service integration for enhanced NLP processing."""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from ..models.task_spec import AIAnalysis, TaskSpec, TaskSize, TaskCategory
from ..models.issue import IssueType, IssuePriority

logger = logging.getLogger(__name__)


class AIService:
    """Base class for AI service integration."""
    
    def analyze_description(self, description: str, context: Optional[Dict[str, Any]] = None) -> AIAnalysis:
        """Analyze description using AI.
        
        Args:
            description: Natural language description
            context: Optional project context
            
        Returns:
            AI analysis results
        """
        raise NotImplementedError("Subclasses must implement analyze_description")


class OpenAIService(AIService):
    """OpenAI GPT integration for task extraction."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key (defaults to env var)
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        # Import openai here to make it optional
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def analyze_description(self, description: str, context: Optional[Dict[str, Any]] = None) -> AIAnalysis:
        """Analyze description using OpenAI GPT.
        
        Args:
            description: Natural language description
            context: Optional project context
            
        Returns:
            AI analysis results
        """
        start_time = time.time()
        
        # Build the prompt
        prompt = self._build_prompt(description, context)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            result = response.choices[0].message.content
            analysis = self._parse_response(result)
            
            # Add metadata
            analysis.ai_model = self.model
            analysis.processing_time = time.time() - start_time
            analysis.confidence_score = 0.85  # GPT-4 generally has high confidence
            
            return analysis
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Return a basic analysis on error
            return self._fallback_analysis(description)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for task extraction."""
        return """You are an expert project manager and software engineer. Your task is to analyze natural language descriptions 
of project requirements and break them down into specific, actionable tasks suitable for GitLab issue tracking.

For each task you identify, determine:
1. A clear, concise title (max 80 characters)
2. The task type (feature, bug, task, documentation, research)
3. Priority level (critical, high, medium, low)
4. Estimated size (small: 1-2 hours, medium: 2-8 hours, large: 1-3 days, xlarge: 3+ days)
5. Any dependencies on other tasks
6. Relevant labels and technologies

Provide your response in JSON format with the following structure:
{
    "summary": "Brief summary of the main objective",
    "main_objective": "Primary goal",
    "sub_objectives": ["List of secondary goals"],
    "suggested_tasks": [
        {
            "title": "Task title",
            "description": "Detailed description",
            "type": "feature|bug|task|documentation|research",
            "priority": "critical|high|medium|low",
            "size": "small|medium|large|xlarge",
            "dependencies": ["Other task titles this depends on"],
            "labels": ["Relevant labels"],
            "technologies": ["Technologies mentioned"]
        }
    ],
    "suggested_milestones": ["Suggested project milestones"],
    "complexity_score": 0.0-1.0,
    "risk_factors": ["Identified risks"],
    "assumptions": ["Key assumptions made"]
}"""
    
    def _build_prompt(self, description: str, context: Optional[Dict[str, Any]]) -> str:
        """Build the prompt for OpenAI."""
        prompt = f"Please analyze the following project requirements and break them down into specific tasks:\n\n{description}"
        
        if context:
            if context.get('existing_issues'):
                prompt += f"\n\nNote: The project already has {len(context['existing_issues'])} open issues."
            
            if context.get('team_members'):
                members = [m.get('name', m.get('username', '')) for m in context['team_members'][:5]]
                prompt += f"\n\nTeam members: {', '.join(members)}"
            
            if context.get('milestones'):
                milestones = [m.get('title', '') for m in context['milestones']]
                prompt += f"\n\nActive milestones: {', '.join(milestones)}"
        
        return prompt
    
    def _parse_response(self, response: str) -> AIAnalysis:
        """Parse OpenAI response into AIAnalysis."""
        try:
            # Try to parse as JSON
            data = json.loads(response)
            
            return AIAnalysis(
                summary=data.get('summary', ''),
                main_objective=data.get('main_objective', ''),
                sub_objectives=data.get('sub_objectives', []),
                suggested_tasks=data.get('suggested_tasks', []),
                suggested_milestones=data.get('suggested_milestones', []),
                suggested_labels=self._extract_all_labels(data.get('suggested_tasks', [])),
                complexity_score=float(data.get('complexity_score', 0.5)),
                risk_factors=data.get('risk_factors', []),
                assumptions=data.get('assumptions', []),
                mentioned_technologies=self._extract_all_technologies(data.get('suggested_tasks', []))
            )
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse OpenAI response as JSON, using fallback parser")
            return self._parse_text_response(response)
    
    def _extract_all_labels(self, tasks: List[Dict]) -> List[str]:
        """Extract all unique labels from tasks."""
        labels = set()
        for task in tasks:
            labels.update(task.get('labels', []))
        return list(labels)
    
    def _extract_all_technologies(self, tasks: List[Dict]) -> List[str]:
        """Extract all unique technologies from tasks."""
        techs = set()
        for task in tasks:
            techs.update(task.get('technologies', []))
        return list(techs)
    
    def _parse_text_response(self, response: str) -> AIAnalysis:
        """Parse a text response when JSON parsing fails."""
        # Basic text parsing fallback
        lines = response.split('\n')
        tasks = []
        
        for line in lines:
            if line.strip().startswith(('-', '*', '•')) or (line.strip() and line[0].isdigit() and '.' in line[:3]):
                # This looks like a task
                task_text = line.strip().lstrip('-*•').lstrip('0123456789.')
                tasks.append({
                    'title': task_text.strip()[:80],
                    'description': task_text.strip(),
                    'type': 'task',
                    'priority': 'medium',
                    'size': 'medium'
                })
        
        return AIAnalysis(
            summary="Parsed from text response",
            main_objective="Complete the described tasks",
            sub_objectives=[],
            suggested_tasks=tasks,
            complexity_score=0.5
        )
    
    def _fallback_analysis(self, description: str) -> AIAnalysis:
        """Create a basic analysis when AI fails."""
        return AIAnalysis(
            summary="AI analysis failed, using basic extraction",
            main_objective="Complete the described requirements",
            sub_objectives=[],
            suggested_tasks=[],
            complexity_score=0.5,
            confidence_score=0.3
        )


class ClaudeService(AIService):
    """Anthropic Claude integration for task extraction."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """Initialize Claude service.
        
        Args:
            api_key: Anthropic API key (defaults to env var)
            model: Model to use
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")
        
        # Import anthropic here to make it optional
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def analyze_description(self, description: str, context: Optional[Dict[str, Any]] = None) -> AIAnalysis:
        """Analyze description using Claude.
        
        Args:
            description: Natural language description
            context: Optional project context
            
        Returns:
            AI analysis results
        """
        start_time = time.time()
        
        # Build the prompt
        prompt = self._build_prompt(description, context)
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=self._get_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response
            result = response.content[0].text
            analysis = self._parse_response(result)
            
            # Add metadata
            analysis.ai_model = self.model
            analysis.processing_time = time.time() - start_time
            analysis.confidence_score = 0.9  # Claude generally has high confidence
            
            return analysis
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            # Return a basic analysis on error
            return self._fallback_analysis(description)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for task extraction."""
        # Similar to OpenAI but can be customized for Claude's strengths
        return """You are an expert project manager and software engineer. Your task is to analyze natural language descriptions 
of project requirements and break them down into specific, actionable tasks suitable for GitLab issue tracking.

Focus on creating clear, implementable tasks with accurate effort estimates and logical dependencies.

For each task you identify, determine:
1. A clear, concise title (max 80 characters)
2. The task type (feature, bug, task, documentation, research)
3. Priority level (critical, high, medium, low)
4. Estimated size (small: 1-2 hours, medium: 2-8 hours, large: 1-3 days, xlarge: 3+ days)
5. Any dependencies on other tasks
6. Relevant labels and technologies

Provide your response in JSON format with the following structure:
{
    "summary": "Brief summary of the main objective",
    "main_objective": "Primary goal",
    "sub_objectives": ["List of secondary goals"],
    "suggested_tasks": [
        {
            "title": "Task title",
            "description": "Detailed description",
            "type": "feature|bug|task|documentation|research",
            "priority": "critical|high|medium|low",
            "size": "small|medium|large|xlarge",
            "dependencies": ["Other task titles this depends on"],
            "labels": ["Relevant labels"],
            "technologies": ["Technologies mentioned"]
        }
    ],
    "suggested_milestones": ["Suggested project milestones"],
    "complexity_score": 0.0-1.0,
    "risk_factors": ["Identified risks"],
    "assumptions": ["Key assumptions made"]
}"""
    
    # The rest of the methods (_build_prompt, _parse_response, etc.) 
    # can be inherited from OpenAIService or implemented similarly
    _build_prompt = OpenAIService._build_prompt
    _parse_response = OpenAIService._parse_response
    _extract_all_labels = OpenAIService._extract_all_labels
    _extract_all_technologies = OpenAIService._extract_all_technologies
    _parse_text_response = OpenAIService._parse_text_response
    _fallback_analysis = OpenAIService._fallback_analysis


def create_ai_service(provider: str = "openai", api_key: Optional[str] = None) -> AIService:
    """Factory function to create AI service.
    
    Args:
        provider: AI provider ('openai' or 'claude')
        api_key: Optional API key
        
    Returns:
        AI service instance
    """
    if provider.lower() == "openai":
        return OpenAIService(api_key)
    elif provider.lower() == "claude":
        return ClaudeService(api_key)
    else:
        raise ValueError(f"Unknown AI provider: {provider}")


def extract_tasks_from_ai_analysis(analysis: AIAnalysis, original_description: str) -> List[TaskSpec]:
    """Convert AI analysis to TaskSpec objects.
    
    Args:
        analysis: AI analysis results
        original_description: Original description text
        
    Returns:
        List of TaskSpec objects
    """
    tasks = []
    
    for i, ai_task in enumerate(analysis.suggested_tasks):
        # Map AI task to TaskSpec
        task = TaskSpec(
            title=ai_task.get('title', f'Task {i+1}'),
            description=ai_task.get('description', ''),
            source_text=original_description,
            extraction_method='ai',
            confidence_score=analysis.confidence_score
        )
        
        # Set type
        type_str = ai_task.get('type', 'task').lower()
        task.task_type = IssueType(type_str) if type_str in [t.value for t in IssueType] else IssueType.TASK
        
        # Set priority
        priority_str = ai_task.get('priority', 'medium').lower()
        task.priority = IssuePriority(priority_str) if priority_str in [p.value for p in IssuePriority] else IssuePriority.MEDIUM
        
        # Set size
        size_str = ai_task.get('size', 'medium').lower()
        task.size = TaskSize(size_str) if size_str in [s.value for s in TaskSize] else TaskSize.MEDIUM
        
        # Set dependencies
        task.dependencies = ai_task.get('dependencies', [])
        
        # Set labels
        task.labels = ai_task.get('labels', [])
        
        # Set technologies
        task.technologies = ai_task.get('technologies', [])
        
        # Determine category based on type
        if task.task_type == IssueType.BUG:
            task.category = TaskCategory.BUGFIX
        elif task.task_type == IssueType.DOCUMENTATION:
            task.category = TaskCategory.DOCUMENTATION
        elif task.task_type == IssueType.RESEARCH:
            task.category = TaskCategory.RESEARCH
        elif 'test' in task.title.lower() or 'testing' in task.labels:
            task.category = TaskCategory.TESTING
        elif 'design' in task.title.lower() or 'ui' in task.labels or 'ux' in task.labels:
            task.category = TaskCategory.DESIGN
        elif 'infrastructure' in task.labels or 'devops' in task.labels:
            task.category = TaskCategory.INFRASTRUCTURE
        else:
            task.category = TaskCategory.IMPLEMENTATION
        
        tasks.append(task)
    
    return tasks