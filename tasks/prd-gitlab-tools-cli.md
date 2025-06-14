# PRD: GitLab Tools CLI

## Introduction/Overview

The GitLab Tools CLI (`glt`) is a unified command-line interface that simplifies executing GitLab management operations through natural language-like commands. Similar to Claude Code, users can type commands in plain English to perform complex GitLab operations without remembering specific script names or parameters. This tool acts as an intelligent wrapper around the existing scripts, making GitLab administration more accessible and efficient.

## Goals

1. Provide a single entry point for all GitLab management operations
2. Enable natural language command execution (e.g., "rename branches in AI projects")
3. Reduce the learning curve for using GitLab tools
4. Maintain operation history and enable command reuse
5. Provide intelligent suggestions and auto-completion

## User Stories

1. **As a DevOps engineer**, I want to type "generate weekly report for all teams" so that I don't need to remember the exact script name and parameters.

2. **As a project manager**, I want to type "create issues from issues folder" so that I can quickly sync my markdown files to GitLab without learning command syntax.

3. **As a team lead**, I want to type "show analytics for project 123" so that I can quickly get project insights without navigating multiple scripts.

4. **As a developer**, I want to type "rename trunk to main in all repos" so that I can modernize branch names across the organization easily.

## Functional Requirements

1. **Command Parser**
   - The system must parse natural language commands and map them to appropriate scripts
   - The system must support command aliases (e.g., "weekly report" = "productivity report" = "team report")
   - The system must handle partial commands and suggest completions

2. **Script Execution**
   - The system must execute the appropriate script with correct parameters
   - The system must show real-time progress for long-running operations
   - The system must capture and display script output clearly

3. **Interactive Mode**
   - The system must provide an interactive REPL (Read-Eval-Print Loop)
   - The system must show a welcome message with example commands
   - The system must support command history (up/down arrows)

4. **Command Mapping**
   - The system must support these command patterns:
     - "rename branches [in group X] [from Y to Z]"
     - "create issues [from folder] [for project X]"
     - "generate dashboard [for groups X,Y,Z]"
     - "analyze project [ID]"
     - "send report [file] to [email]"
     - "weekly report [for groups X,Y,Z]"
     - "sync issues [for project X]"
     - "export analytics [for projects X,Y,Z]"

5. **Help System**
   - The system must provide contextual help with "help" or "?"
   - The system must show command examples
   - The system must explain available options for each command

6. **Configuration**
   - The system must read from existing .env configuration
   - The system must support command shortcuts/aliases in config
   - The system must remember frequently used project IDs and group names

7. **Output Formatting**
   - The system must use colored output for better readability
   - The system must show progress indicators for long operations
   - The system must summarize results clearly

## Non-Goals (Out of Scope)

1. This tool will NOT replace the individual scripts (they remain independently usable)
2. This tool will NOT add new GitLab functionality (only wraps existing scripts)
3. This tool will NOT provide a web interface or API
4. This tool will NOT handle GitLab authentication (relies on existing .env setup)
5. This tool will NOT support complex scripting or conditionals

## Design Considerations

- **Entry Point**: Single executable `glt` command
- **User Interface**: Terminal-based with colored output using existing progress indicators
- **Command Style**: Natural language with smart parsing
- **Error Messages**: Friendly, suggesting correct command format
- **Integration**: Seamless execution of existing scripts without modification

## Technical Considerations

1. **Architecture**: Thin wrapper around existing scripts
2. **Dependencies**: Reuse existing utilities (config, logger, progress)
3. **Command Parsing**: Simple keyword matching with fuzzy search
4. **Process Management**: Use subprocess to run existing scripts
5. **State**: Stateless except for command history
6. **Installation**: Add to PATH via setup script or pip install

## Success Metrics

1. Time to execute common operations reduced by 50%
2. New team members can use GitLab tools within 5 minutes
3. 80% of operations can be completed without referring to documentation
4. Error rate reduced by 30% due to intelligent parameter validation

## Open Questions

1. Should the CLI support batch operations from a file?
2. Should we add tab completion for project/group names?
3. Should command history be shared across sessions?
4. Should we support command abbreviations (e.g., "wb" for "weekly report")?

## Example Usage

```bash
$ glt
GitLab Tools CLI v1.0
Type 'help' for available commands or 'exit' to quit.

> rename branches in AI-ML-Services from trunk to main
🔄 Renaming branches in group 'AI-ML-Services'...
✓ Successfully renamed: 15 branches
⏭️ Skipped: 3 (no trunk branch)
❌ Failed: 0

> create issues for project 123
📁 Found 5 issue files in 'issues/' folder
✓ Created issue #142: User Authentication
✓ Created issue #143: Fix Memory Leak
✓ All issues created successfully!

> generate weekly report for groups 1,2,3 and email to team@company.com
📊 Generating weekly productivity report...
✓ Report generated: 45 commits, 12 MRs, 8 issues closed
📧 Sending email to team@company.com...
✓ Email sent successfully!

> help
Available commands:
  • rename branches [in <group>] [from <old> to <new>]
  • create issues [for project <id>] [from <folder>]
  • generate dashboard [for groups <ids>]
  • analyze project <id>
  • weekly report [for groups <ids>] [email to <addresses>]
  • sync issues [for project <id>]
  
Type 'help <command>' for detailed information.

> exit
Goodbye! 👋
```