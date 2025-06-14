## Relevant Files

- `glt.py` - Main entry point for the CLI application that handles the REPL loop
- `tests/test_glt.py` - Integration tests for the main CLI
- `src/cli/command_parser.py` - Natural language command parser with fuzzy matching
- `tests/unit/cli/test_command_parser.py` - Unit tests for command parser
- `src/cli/command_executor.py` - Executes parsed commands by calling appropriate scripts
- `tests/unit/cli/test_command_executor.py` - Unit tests for command executor
- `src/cli/command_registry.py` - Defines command patterns and script mappings
- `tests/unit/cli/test_command_registry.py` - Unit tests for command registry
- `src/cli/repl.py` - Interactive REPL implementation with history support
- `tests/unit/cli/test_repl.py` - Unit tests for REPL
- `src/cli/help_system.py` - Help command implementation and documentation
- `tests/unit/cli/test_help_system.py` - Unit tests for help system
- `setup.py` - Package setup for pip installation
- `bin/glt` - Shell wrapper for the CLI executable

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `MyComponent.py` and `MyComponent.test.py` in the same directory).
- Use `npx jest [optional/path/to/test/file]` to run tests. Running without a path executes all tests found by the Jest configuration.

## Tasks

- [ ] 1.0 Set up project structure and core CLI infrastructure
  - [x] 1.1 Create `src/cli/` directory structure for CLI-specific modules
  - [x] 1.2 Create `glt.py` main entry point with basic argument parsing
  - [x] 1.3 Set up `setup.py` for pip installation with entry points
  - [x] 1.4 Create `bin/glt` shell wrapper for system-wide installation
  - [x] 1.5 Add CLI dependencies to requirements.txt (prompt_toolkit, click, etc.)
  - [ ] 1.6 Create basic logging configuration for CLI operations

- [ ] 2.0 Implement command parsing and pattern matching
  - [ ] 2.1 Create `command_registry.py` with command pattern definitions
  - [ ] 2.2 Define regex patterns for each command type (rename, create, generate, etc.)
  - [ ] 2.3 Implement `command_parser.py` with natural language parsing logic
  - [ ] 2.4 Add fuzzy matching for command recognition using difflib
  - [ ] 2.5 Create command alias mapping (weekly report = productivity report)
  - [ ] 2.6 Implement parameter extraction from natural language commands
  - [ ] 2.7 Add validation for extracted parameters (project IDs, group names)
  - [ ] 2.8 Write comprehensive unit tests for parser edge cases

- [ ] 3.0 Create command execution engine
  - [ ] 3.1 Implement `command_executor.py` base class with execute method
  - [ ] 3.2 Create script mapping to translate parsed commands to script calls
  - [ ] 3.3 Build subprocess wrapper to execute existing scripts safely
  - [ ] 3.4 Implement real-time output capture and display from scripts
  - [ ] 3.5 Add progress indicator pass-through from existing progress utilities
  - [ ] 3.6 Handle script errors gracefully with user-friendly messages
  - [ ] 3.7 Create execution result formatting for consistent output
  - [ ] 3.8 Add dry-run support for all commands

- [ ] 4.0 Build interactive REPL with history support
  - [ ] 4.1 Implement `repl.py` with prompt_toolkit for advanced terminal UI
  - [ ] 4.2 Create welcome banner with version and example commands
  - [ ] 4.3 Add command history with arrow key navigation
  - [ ] 4.4 Implement tab completion for common commands and parameters
  - [ ] 4.5 Add syntax highlighting for commands as they're typed
  - [ ] 4.6 Create session history persistence in ~/.glt_history
  - [ ] 4.7 Implement special commands (exit, clear, history)
  - [ ] 4.8 Add command suggestion on partial/incorrect input
  - [ ] 4.9 Create colored output using existing progress utilities

- [ ] 5.0 Implement help system and documentation
  - [ ] 5.1 Create `help_system.py` with command documentation
  - [ ] 5.2 Implement contextual help for each command pattern
  - [ ] 5.3 Add example usage for every supported command
  - [ ] 5.4 Create "help <command>" functionality for detailed help
  - [ ] 5.5 Generate command reference from registry automatically
  - [ ] 5.6 Add interactive tutorial mode for new users
  - [ ] 5.7 Create man page for system installation
  - [ ] 5.8 Write integration tests for complete workflows