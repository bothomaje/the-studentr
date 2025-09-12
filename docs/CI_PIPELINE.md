# CI Pipeline Documentation

## Overview

This repository now includes a comprehensive CI pipeline (`ci.yml`) that provides:
- Cross-platform building (macOS and Windows)
- Code quality checks with multiple linters
- Smart change detection and selective job execution
- Manual workflow controls
- Rich job summaries and error reporting
- Build artifact uploads

## Manual Workflow Controls

The pipeline can be triggered manually with these options:

- **Force run all jobs**: Ignores change detection and runs everything
- **Run linting jobs**: Toggle linting on/off
- **Run test jobs**: Toggle test jobs on/off  
- **Run build jobs**: Toggle build jobs on/off
- **Run UML rendering**: Toggle UML diagram rendering on/off
- **Force full lint scope**: Run linting on entire repository instead of just changed files
- **Fail on SQLFluff violations**: Make SQL linting failures break the build

## Automatic Triggers

The pipeline automatically runs on:
- Pushes to the `main` branch
- Pull requests targeting the `main` branch

Based on file changes, it will selectively run:
- **Linting**: When Python, YAML, SQL, or shell files change
- **Testing**: When Python, database, or UI files change  
- **Building**: When Python or UI files change
- **UML**: When PlantUML diagram files change

## Build Artifacts

When builds succeed, the following artifacts are uploaded:

### macOS Build
- `.app` application bundle
- `.dmg` installer (if create-dmg is available)

### Windows Build  
- Executable directory containing the built application
- `.zip` package for easy distribution

Artifacts are retained for 30 days and can be downloaded from the workflow run.

## Application Output

Both build jobs include a step that runs the built application and displays output in the job summary, allowing you to verify the application works correctly.

## Code Quality Checks

The pipeline includes comprehensive linting:
- **Python**: Ruff linter with GitHub annotations
- **YAML**: yamllint for configuration files
- **Shell Scripts**: ShellCheck for bash scripts
- **SQL**: SQLFluff for database queries

## Requirements Adaptation

Note: The original requirements mentioned C++ code with clang-tidy and clang-format, but this is a Python project. The pipeline has been adapted to provide equivalent functionality:
- Python linting (ruff) instead of clang-tidy
- YAML formatting checks instead of clang-format
- Cross-platform Python application builds instead of C++ compilation
- All other requirements (manual controls, change detection, artifact uploads, job summaries) are fully implemented as requested.