"""
Command Parser for GitLab Tools CLI.

Parses natural language commands into structured command objects.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

from .command_registry import CommandRegistry, CommandPattern


@dataclass
class ParsedCommand:
    """Represents a parsed command with its parameters."""
    
    command: CommandPattern
    parameters: Dict[str, str]
    confidence: float
    original_input: str
    
    def __str__(self):
        return f"Command: {self.command.description}, Params: {self.parameters}, Confidence: {self.confidence:.2f}"


class CommandParser:
    """Parser for natural language commands."""
    
    def __init__(self):
        self.registry = CommandRegistry()
        self.command_history: List[ParsedCommand] = []
    
    def parse(self, user_input: str) -> Optional[ParsedCommand]:
        """
        Parse a natural language command into a structured command.
        
        Args:
            user_input: The user's command string
            
        Returns:
            ParsedCommand object or None if no match found
        """
        if not user_input or not user_input.strip():
            return None
        
        user_input = user_input.strip()
        
        # Try registry-based matching first (exact patterns)
        result = self.registry.find_command(user_input)
        if result:
            command, params = result
            parsed_command = ParsedCommand(
                command=command,
                parameters=params,
                confidence=1.0,  # Exact match
                original_input=user_input
            )
            self.command_history.append(parsed_command)
            return parsed_command
        
        # Try fuzzy matching with similarity scoring
        fuzzy_result = self._fuzzy_parse(user_input)
        if fuzzy_result:
            self.command_history.append(fuzzy_result)
            return fuzzy_result
        
        return None
    
    def _fuzzy_parse(self, user_input: str) -> Optional[ParsedCommand]:
        """
        Perform fuzzy matching when exact parsing fails.
        
        Args:
            user_input: The user's command string
            
        Returns:
            ParsedCommand with confidence score or None
        """
        best_match = None
        best_confidence = 0.0
        
        for command in self.registry.get_all_commands():
            # Check against examples
            for example in command.examples:
                confidence = self._calculate_similarity(user_input, example)
                if confidence > best_confidence and confidence >= 0.6:  # Minimum threshold
                    best_confidence = confidence
                    best_match = command
            
            # Check against aliases
            for alias in command.aliases:
                confidence = self._calculate_similarity(user_input, alias)
                if confidence > best_confidence and confidence >= 0.5:  # Lower threshold for aliases
                    best_confidence = confidence
                    best_match = command
        
        if best_match:
            # Extract parameters using various strategies
            params = self._extract_parameters(user_input, best_match)
            
            return ParsedCommand(
                command=best_match,
                parameters=params,
                confidence=best_confidence,
                original_input=user_input
            )
        
        return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        # Normalize both strings
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # Use SequenceMatcher for basic similarity
        basic_similarity = SequenceMatcher(None, text1, text2).ratio()
        
        # Bonus for keyword matches
        words1 = set(text1.split())
        words2 = set(text2.split())
        common_words = words1.intersection(words2)
        keyword_bonus = len(common_words) / max(len(words1), len(words2)) * 0.3
        
        return min(basic_similarity + keyword_bonus, 1.0)
    
    def _extract_parameters(self, user_input: str, command: CommandPattern) -> Dict[str, str]:
        """
        Extract parameters from user input for a given command.
        
        Args:
            user_input: The original user input
            command: The matched command pattern
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {}
        
        # Try to extract parameters using the command's regex pattern
        pattern = re.compile(command.pattern, re.IGNORECASE)
        match = pattern.search(user_input)
        if match:
            params.update(match.groupdict())
        
        # Additional parameter extraction strategies
        params.update(self._extract_common_parameters(user_input))
        
        # Clean up parameter values
        cleaned_params = {}
        for key, value in params.items():
            if value is not None:
                cleaned_params[key] = value.strip()
        
        return cleaned_params
    
    def _extract_common_parameters(self, user_input: str) -> Dict[str, str]:
        """Extract common parameters that appear across multiple commands."""
        params = {}
        
        # Project ID patterns
        project_patterns = [
            r'project\s+(\d+)',
            r'project\s+id\s+(\d+)',
            r'for\s+project\s+(\d+)',
            r'in\s+project\s+(\d+)'
        ]
        for pattern in project_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                params['project_id'] = match.group(1)
                break
        
        # Group ID patterns
        group_patterns = [
            r'group\s+([\d,\s]+)',
            r'groups\s+([\d,\s]+)',
            r'for\s+groups?\s+([\d,\s]+)',
            r'in\s+groups?\s+([\d,\s]+)'
        ]
        for pattern in group_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                params['group_ids'] = match.group(1)
                break
        
        # Email patterns
        email_pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'
        email_match = re.search(email_pattern, user_input)
        if email_match:
            params['email'] = email_match.group(1)
        
        # File patterns
        file_patterns = [
            r'file\s+(\S+\.\w+)',
            r'report\s+(\S+\.\w+)',
            r'send\s+(\S+\.\w+)',
            r'(\S+\.(pdf|html|txt|csv|json))'
        ]
        for pattern in file_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                params['file'] = match.group(1)
                break
        
        # Branch name patterns
        branch_patterns = [
            r'from\s+(\S+)\s+to\s+(\S+)',
            r'branch\s+(\S+)',
            r'branches?\s+(\S+)'
        ]
        for pattern in branch_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    params['old_branch'] = match.group(1)
                    params['new_branch'] = match.group(2)
                else:
                    params['branch'] = match.group(1)
                break
        
        return params
    
    def get_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions based on partial input."""
        if not partial_input or len(partial_input) < 2:
            # Return most common commands
            return [
                "create issues",
                "generate dashboard", 
                "weekly report",
                "analyze project",
                "sync issues",
                "rename branches"
            ]
        
        return self.registry.get_command_suggestions(partial_input)
    
    def get_command_help(self, command_name: str) -> Optional[CommandPattern]:
        """Get help information for a specific command."""
        # Try to find the command by name or alias
        for command in self.registry.get_all_commands():
            if (command_name.lower() in command.pattern.lower() or
                any(command_name.lower() in alias.lower() for alias in command.aliases)):
                return command
        
        return None
    
    def get_all_commands(self) -> List[CommandPattern]:
        """Get all available commands."""
        return self.registry.get_all_commands()
    
    def validate_parameters(self, parsed_command: ParsedCommand) -> Tuple[bool, List[str]]:
        """
        Validate that a parsed command has all required parameters.
        
        Args:
            parsed_command: The parsed command to validate
            
        Returns:
            Tuple of (is_valid, list_of_missing_params)
        """
        missing_params = []
        invalid_params = []
        
        # Check required parameters
        if parsed_command.command.required_params:
            for param in parsed_command.command.required_params:
                if param not in parsed_command.parameters or not parsed_command.parameters[param]:
                    missing_params.append(param)
        
        # Validate parameter formats
        for param_name, param_value in parsed_command.parameters.items():
            if not param_value:  # Skip empty values
                continue
                
            # Validate project IDs
            if param_name in ['project_id'] and not re.match(r'^\d+$', param_value):
                invalid_params.append(f"{param_name}: '{param_value}' is not a valid project ID")
            
            # Validate group IDs
            if param_name in ['group_ids'] and not re.match(r'^[\d,\s]+$', param_value):
                invalid_params.append(f"{param_name}: '{param_value}' is not a valid group ID list")
            
            # Validate email addresses
            if param_name in ['email'] and not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', param_value):
                invalid_params.append(f"{param_name}: '{param_value}' is not a valid email address")
            
            # Validate file extensions
            if param_name in ['file'] and not re.match(r'.*\.\w+$', param_value):
                invalid_params.append(f"{param_name}: '{param_value}' does not appear to be a valid file")
        
        all_errors = missing_params + invalid_params
        return len(all_errors) == 0, all_errors 