# Product Requirements Document: Direct Script Commands Interface

## Introduction/Overview

Enhance the GitLab Tools CLI to support direct script command execution, providing a streamlined interface that maps CLI commands directly to existing Python scripts. This addresses the need for a more predictable, script-centric command interface alongside the existing natural language processing.

**Goal:** Create a unified CLI interface where users can execute GitLab operations using direct script names with standardized command-line flags, making all scripts accessible from a single entry point.

## Goals

1. Provide direct access to all GitLab scripts through standardized CLI commands
2. Maintain consistent parameter naming and behavior across all commands
3. Offer both direct script commands and natural language commands
4. Simplify script discovery and usage through integrated help system
5. Ensure backward compatibility with existing natural language interface

## User Stories

- **As a developer**, I want to type `rename_branches --groups "AI-ML-Services" --old-branch trunk --new-branch main` so that I can rename branches with the same syntax as the existing scripts
- **As a team lead**, I want to run `generate_executive_dashboard --groups 1,2,3 --days 30` so that I can quickly generate reports using familiar parameters
- **As a project manager**, I want to execute `sync_issues my-project --dry-run` so that I can preview issue creation before execution
- **As a DevOps engineer**, I want to run `generate_executive_dashboard --groups 1721,1267,1269 --output report.html` then `send_report_email report.html team@company.com "Weekly Report"` so that I can automate the complete reporting workflow
- **As any user**, I want to type `rename_branches --help` so that I can see exactly what parameters are available for each script

## Functional Requirements

### Core Command Structure
1. **FR-1:** CLI must support direct script execution using underscore naming: `script_name --param value`
2. **FR-2:** All script commands must use space-separated flag format: `--flag value` (not `--flag=value`)
3. **FR-3:** CLI must execute the corresponding Python script in the `scripts/` directory
4. **FR-4:** Commands must pass parameters directly to the underlying scripts

### Parameter Mapping
5. **FR-5:** Map CLI flags directly to existing script parameters:
   - `--groups` for group names (space-separated) or group IDs (comma-separated)
   - `--old-branch` and `--new-branch` for branch rename operations
   - `--project` and `--group` for analytics target specification
   - `--output` for output file paths
   - `--days` for analysis time periods
   - `--dry-run` for preview mode across applicable scripts
6. **FR-6:** Preserve existing script parameter formats and validation

### Available Commands
7. **FR-7:** Implement direct commands for all existing scripts (mapping to actual script interfaces):
   - `rename_branches --groups <group_names> [--old-branch <old>] [--new-branch <new>] [--dry-run] [--report <file>]`
   - `generate_executive_dashboard --groups <group_ids> [--output <file>] [--days <days>] [--team-name <name>]`
   - `sync_issues <project_id> [--issues-dir <path>] [--use-api] [--dry-run] [--generate-script]`
   - `send_report_email <html_file> <recipient> <subject>`
   - `analyze_projects --project <project> [--group <group>] [--format <format>] [--output <file>]`
   - `export_analytics <project> [--output <file>] [--trends] [--days <days>]`

### Help System
8. **FR-8:** Each command must support `--help` flag showing usage, parameters, and examples
9. **FR-9:** Running command without parameters must show brief usage information
10. **FR-10:** Main CLI must list all available direct commands with `help` or `--help`

### Integration
11. **FR-11:** Direct script commands must coexist with existing natural language commands
12. **FR-12:** Direct commands take precedence when input matches exact script name pattern
13. **FR-13:** Maintain existing REPL functionality for both command types

### Error Handling
14. **FR-14:** Provide clear error messages for missing required parameters
15. **FR-15:** Show command usage examples when parameters are invalid
16. **FR-16:** Validate parameter formats (e.g., numeric IDs, valid email addresses)

## Non-Goals (Out of Scope)

- **NG-1:** Remove or deprecate existing natural language command interface
- **NG-2:** Modify existing Python scripts' internal logic or parameters
- **NG-3:** Add new GitLab operations beyond existing scripts
- **NG-4:** Implement command chaining or piping between scripts
- **NG-5:** Add configuration file support for default parameters

## Technical Considerations

- **TC-1:** Extend existing `CommandRegistry` to support exact script name pattern matching
- **TC-2:** Create direct parameter pass-through to preserve existing script interfaces
- **TC-3:** Leverage existing `CommandExecutor` for script execution with parameter mapping
- **TC-4:** Integrate with current help system to display script-specific help
- **TC-5:** Maintain colored output and progress indicators from existing implementation
- **TC-6:** Preserve existing script parameter validation and error handling
- **TC-7:** Support both positional and optional parameters as defined in existing scripts

## Success Metrics

1. **User Adoption:** 80% of power users prefer direct commands for repetitive tasks
2. **Error Reduction:** 50% fewer command syntax errors compared to natural language
3. **Discovery Time:** New users can execute any script within 2 minutes using help system
4. **Consistency:** 100% of commands follow standardized parameter naming conventions

## Open Questions

- Should we add command aliases (e.g., `gen_dashboard` for `generate_executive_dashboard`)?
- Do we need tab completion for parameter values (project IDs, group names)?
- Should we extend the existing help system to show examples from the README?
- How should we handle script-specific parameters that don't follow common patterns?
- Should we support chaining commands (e.g., generate dashboard then email automatically)? 