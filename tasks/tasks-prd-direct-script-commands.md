## Relevant Files

- `src/cli/command_registry.py` - ✅ Extended with DirectScriptPattern dataclass, script discovery, and direct command support
- `src/cli/command_parser.py` - ✅ Updated with DirectScriptCommand dataclass, direct script parsing, and parameter validation
- `src/cli/command_executor.py` - ✅ Enhanced with execute_direct_script method and script-specific parameter formatting
- `src/cli/help_system.py` - ✅ Integrated ScriptHelpExtractor class and standardized help format for direct commands
- `src/cli/repl.py` - ✅ Updated with enhanced tab completion, dual command support, and new special commands
- `tests/unit/cli/test_direct_script_commands.py` - Unit tests for direct script command functionality (to be created)
- `tests/integration/test_script_integration.py` - Integration tests for script execution (to be created)

### Notes

- Direct script commands should coexist with existing natural language commands
- Parameter validation and error handling should be preserved from existing scripts
- Use `pytest tests/unit/cli/` for unit tests and `pytest tests/integration/` for integration tests
- All changes must maintain backward compatibility with existing CLI interface

## Tasks

- [x] 1.0 Extend Command Registry for Direct Script Support
  - [x] 1.1 Add DirectScriptPattern dataclass with script name, path, and parameter definitions
  - [x] 1.2 Create script discovery method to scan scripts/ directory and extract parameter info
  - [x] 1.3 Add register_direct_script method to CommandRegistry class
  - [x] 1.4 Define parameter mappings for each existing script (rename_branches, generate_executive_dashboard, etc.)
  - [x] 1.5 Implement exact script name pattern matching (e.g., "rename_branches" matches directly)
  - [x] 1.6 Add get_direct_script_commands method to list all available direct commands
  - [x] 1.7 Update find_command method to check direct scripts first before natural language patterns

- [x] 2.0 Update Command Parser for Exact Script Matching
  - [x] 2.1 Add is_direct_script_command method to detect exact script name matches
  - [x] 2.2 Create parse_direct_script_command method to extract parameters from direct commands
  - [x] 2.3 Implement parameter validation for each script's required and optional parameters
  - [x] 2.4 Add support for positional arguments (e.g., sync_issues PROJECT_ID)
  - [x] 2.5 Handle space-separated flag format (--flag value) parsing
  - [x] 2.6 Add DirectScriptCommand dataclass to represent parsed direct commands
  - [x] 2.7 Update main parse method to prioritize direct script commands over natural language

- [x] 3.0 Enhance Command Executor for Parameter Pass-through
  - [x] 3.1 Add execute_direct_script method to CommandExecutor class
  - [x] 3.2 Create parameter mapping logic to convert CLI flags to script arguments
  - [x] 3.3 Implement script-specific parameter formatting (groups as space-separated vs comma-separated)
  - [x] 3.4 Add support for boolean flags (--dry-run, --use-api) without values
  - [x] 3.5 Handle positional arguments and convert to proper script parameters
  - [x] 3.6 Preserve existing script error handling and output formatting
  - [x] 3.7 Add validation for required parameters before script execution

- [x] 4.0 Integrate Script-Specific Help System
  - [x] 4.1 Create ScriptHelpExtractor class to parse help from existing scripts
  - [x] 4.2 Add get_script_help method to extract --help output from each script
  - [x] 4.3 Create standardized help format template for direct commands
  - [x] 4.4 Implement generate_direct_command_help method in HelpSystem class
  - [x] 4.5 Add show_script_usage method for displaying usage examples
  - [x] 4.6 Update main help command to include direct script commands section  
  - [x] 4.7 Handle --help flag for individual direct commands (e.g., "rename_branches --help")

- [x] 5.0 Update REPL Interface for Dual Command Support
  - [x] 5.1 Update GitLabCompleter to include direct script command names in tab completion
  - [x] 5.2 Add direct command parameter completion (flags and values)
  - [x] 5.3 Update command suggestions to include both natural language and direct commands
  - [x] 5.4 Modify process_command method to handle both command types
  - [x] 5.5 Update welcome banner to mention direct script command availability
  - [x] 5.6 Add "list-commands" special command to show all available direct commands
  - [x] 5.7 Test and ensure both command types work seamlessly in the same REPL session 