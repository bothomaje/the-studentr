# CI Pipeline Technical Documentation

This document provides comprehensive technical documentation for the CI/CD pipeline defined in `.github/workflows/pipeline.yml`. The pipeline orchestrates automated testing, validation, and builds for the the-studentr application.

## Pipeline Overview

The CI pipeline consists of 8 main jobs that execute based on change detection and dependency relationships:

1. **detect** - Change detection and file filtering
2. **lint** - Code quality validation across multiple languages
3. **plantuml** - UML diagram rendering and commit
4. **db-validate** - Database schema and DAL testing
5. **ui-logic-validate** - UI and business logic testing
6. **build-macos** - macOS application build and packaging
7. **build-windows** - Windows application build and packaging
8. **pipeline-summary** - Overall pipeline status aggregation

## Pipeline Triggers

The pipeline activates on:
- **Push events** to the `main` branch
- **Pull request events** targeting the `main` branch  
- **Manual dispatch** with configurable parameters:
  - `run_all`: Force execution of all jobs regardless of changes
  - `full_lint`: Force full repository linting scope
  - `enforce_sqlfluff`: Treat SQLFluff violations as failures

## Concurrency Control

Uses `pipeline-${{ github.ref }}` concurrency group with `cancel-in-progress: true` to prevent multiple pipeline runs on the same branch.

## Job Specifications

### 1. Change Detection (`detect`)

**Purpose**: Analyzes changed files to determine which downstream jobs should execute.

**Technology**: Uses `dorny/paths-filter@v3` with JSON file listing.

**File Categories Tracked**:
- **Python** (`py`): `app/**/*.py`, `scripts/**/*.py`, `tests/**/*.py`
- **Database** (`db`): `db/**`, `scripts/**`, `app/dal/**`, `app/config/env.py`, `requirements.txt`
- **UML** (`uml`): `docs/diagrams/**/*.puml`
- **UI/Logic** (`ui`): `app/ui_adapters/**/*.py`, `app/**/*.ui`, `app/**/*.qml`, `app/**/*.py` (excluding DAL/config)
- **YAML** (`yaml`): `**/*.y?(a)ml`
- **Shell** (`sh`): `**/*.sh`
- **SQL** (`sql`): `db/**/*.sql`, `scripts/**/*.sql`

**Outputs**: Boolean flags and file lists for each category, consumed by downstream jobs.

**Summary Generation**: Creates expandable sections showing detected changes per file type.

### 2. Code Quality Validation (`lint`)

**Purpose**: Validates code quality across Python, YAML, Shell, and SQL files.

**Dependencies**: Requires `detect` job completion.

**Execution Strategy**: 
- **First run** (no cache) or manual force: Full repository scan
- **Subsequent runs**: Changed files only (based on detect outputs)

**Tools and Configuration**:

#### Python (Ruff)
- **Version**: `ruff==0.6.*`
- **Output**: JSON format for structured error reporting
- **Scope**: Full repo or changed Python files only

#### YAML (yamllint)
- **Tool**: System yamllint package
- **Output**: Text format with file:line:column details
- **Scope**: Full repo or changed YAML files only

#### Shell (ShellCheck)
- **Tool**: System shellcheck package
- **Pattern**: Discovers `**/*.sh` files using bash globbing
- **Output**: Text format with detailed violation descriptions

#### SQL (SQLFluff)
- **Version**: `sqlfluff==3.*`
- **Dialect**: MySQL (configured via `.sqlfluff` file)
- **Output**: JSON format with violation details
- **Behavior**: Violations logged but don't fail job unless `enforce_sqlfluff=1`
- **Scope**: `db` and `scripts` directories

**Caching**: Uses `lint-baseline-v1` cache key to track first-run status.

**Error Handling**: Each tool captures output to dedicated files, environment variables track failure states.

**Summary Generation**: Provides detailed breakdown per tool with expandable error sections and actionable guidance.

**Artifact Collection**: On failure, uploads `lint-failure-logs` containing all tool outputs.

### 3. UML Diagram Rendering (`plantuml`)

**Purpose**: Renders PlantUML diagrams to SVG format and commits results.

**Dependencies**: Requires `lint` job success.

**Trigger Condition**: Executes when UML files change or manual `run_all=true`.

**Technology Stack**:
- **Java**: Temurin JDK 17
- **PlantUML**: Latest release JAR
- **Graphviz**: System package for diagram rendering

**Process**:
1. Downloads latest PlantUML JAR
2. Discovers `docs/diagrams/**/*.puml` files
3. Renders each to SVG format
4. Auto-commits results with message "chore(diagrams): render PlantUML"

**Permissions**: Requires `contents: write` for committing rendered diagrams.

### 4. Database Validation (`db-validate`)

**Purpose**: Validates database schema, DAL functionality, and data model integrity.

**Dependencies**: Requires `lint` job success.

**Trigger Condition**: Executes when database-related files change or manual `run_all=true`.

**Infrastructure**:
- **MySQL Service**: Version 9.0 container
- **Database**: `the_studentr` with root password from secrets
- **Health Checks**: 30 retries with 5-second intervals
- **Network**: Exposed on port 3306

**Environment Configuration**:
```
SA_DB_HOST=127.0.0.1
SA_DB_PORT=3306  
SA_DB_USER=root
SA_DB_PASS=${{ secrets.CI_DB_ROOT_PASS }}
SA_DB_NAME=the_studentr
```

**Validation Steps**:

#### Database Setup
- **Script**: `python -m scripts.setup_db`
- **Purpose**: Initialize schema and base data
- **Output**: `db-setup.log`

#### DAL Smoke Tests
- **Script**: `python -m scripts.dal_smoke`
- **Purpose**: Validate Data Access Layer connectivity and basic operations
- **Output**: `dal-smoke.log`

#### CI Smoke Tests  
- **Script**: `python -m scripts.ci_smoke`
- **Purpose**: CI-specific validation routines
- **Output**: `ci-smoke.log`

#### Unit Tests
- **Framework**: pytest with quiet mode and short traceback
- **Output**: `pytest-output.log` and `pytest-results.xml`
- **Scope**: All database and DAL tests

**Error Handling**: Each step captures detailed logs and tracks failure states in environment variables.

**Summary Generation**: Provides status breakdown per validation step with expandable error logs.

**Artifact Collection**: On failure, uploads `db-validation-failure-logs` with all validation outputs.

### 5. UI and Logic Validation (`ui-logic-validate`)

**Purpose**: Validates user interface components and business logic without database dependencies.

**Dependencies**: Requires both `lint` and `db-validate` job success.

**Trigger Condition**: Executes when UI/logic files change, with conditional logic:
- Runs if UI changes detected AND either no DB changes OR DB validation succeeded
- Manual `run_all=true` overrides change detection

**Technology Stack**:
- **Python**: 3.11 with pip caching
- **Testing**: pytest and pytest-qt for PyQt5 UI testing
- **Scope**: Excludes database and schema tests (`-k "not db and not schema"`)

**Process**:
1. Install dependencies including pytest-qt for UI testing
2. Configure PYTHONPATH for module resolution
3. Execute UI/logic test suite with structured output

**Output Formats**:
- **Log**: `ui-pytest-output.log` with detailed test results
- **JUnit XML**: `ui-pytest-results.xml` for structured reporting

**Summary Generation**: Provides test status with expandable failure details and local testing guidance.

**Artifact Collection**: On failure, uploads `ui-validation-failure-logs` with test outputs.

### 6. macOS Application Build (`build-macos`)

**Purpose**: Builds standalone macOS application bundle and optional DMG installer.

**Dependencies**: Requires `lint`, `db-validate`, and `ui-logic-validate` job success.

**Trigger Condition**: Executes when UI validation succeeds OR no UI changes detected, with manual override.

**Technology Stack**:
- **Platform**: macOS-latest runner
- **Python**: 3.11 with pip caching
- **Build Tool**: PyInstaller 6.6.*
- **DMG Creation**: Homebrew create-dmg (optional)

**Build Process**:

#### Application Bundle
- **Entry Point**: `app/main.py`
- **Mode**: Windowed (GUI application)
- **Output**: `dist/the-studentr.app`
- **Logging**: Detailed build log in `build.log`

#### DMG Installer (Optional)
- **Tool**: create-dmg from Homebrew
- **Continue on Error**: DMG creation failure doesn't fail the job
- **Output**: `dist/the-studentr.dmg`
- **Logging**: DMG creation log in `dmg-creation.log`

**Error Handling**: 
- PyInstaller failures halt the job with detailed error logging
- DMG failures are logged but don't affect job success

**Summary Generation**: Provides build status, file listings, and detailed error information.

**Artifact Collection**: 
- **Success**: Uploads built .app and .dmg files
- **Failure**: Uploads `macOS-build-failure-logs` with build and DMG logs

### 7. Windows Application Build (`build-windows`)

**Purpose**: Builds standalone Windows application executable.

**Dependencies**: Requires `lint`, `db-validate`, and `ui-logic-validate` job success.

**Trigger Condition**: Executes when UI validation succeeds OR no UI changes detected, with manual override.

**Technology Stack**:
- **Platform**: windows-latest runner
- **Python**: 3.11 with pip caching
- **Build Tool**: PyInstaller 6.6.*

**Build Process**:

#### Application Executable
- **Entry Point**: `app/main.py`
- **Mode**: Windowed (GUI application)
- **Output**: `dist/the-studentr.exe` and supporting files
- **Logging**: Detailed build log in `build.log`

**Error Handling**: 
- PyInstaller failures halt the job with detailed error logging
- Uses bash shell for consistent error handling across platforms

**Summary Generation**: Provides build status, file listings, and detailed error information.

**Artifact Collection**: 
- **Success**: Uploads built .exe and supporting files
- **Failure**: Uploads `Windows-build-failure-logs` with build logs

### 8. Pipeline Summary (`pipeline-summary`)

**Purpose**: Aggregates results from all jobs and provides comprehensive pipeline status.

**Dependencies**: Waits for all jobs (always executes regardless of individual job results).

**Technology**: Bash scripting with conditional status evaluation.

**Summary Components**:

#### Job Results Table
Displays status for each job:
- 🔍 Change Detection
- 🧹 Lint  
- 📊 UML Rendering
- 🗄️ Database Validation
- 🖥️ UI/Logic Validation
- 🍎 macOS Build
- 🪟 Windows Build

**Status Indicators**:
- ✅ Success: Job completed successfully
- ❌ Failed: Job encountered errors
- ⏭️ Skipped: Job didn't execute due to conditions

#### Overall Pipeline Status
- **Success**: All critical jobs passed
- **Failure**: One or more critical jobs failed

#### Recommendations
Provides specific guidance based on pipeline outcome:
- **Success**: Deployment readiness confirmation
- **Failure**: Debugging steps and artifact references

#### Artifact Summary
Lists available artifacts from the pipeline run for investigation and deployment.

## Error Reporting and Debugging

### Error Capture Strategy
Each job implements comprehensive error capture:
- **Tool Output**: Structured JSON or text format logs
- **Environment Variables**: Track failure states across steps
- **Exit Code Handling**: Proper error propagation while capturing diagnostics

### Summary Generation
All jobs generate detailed summaries including:
- **Status Indicators**: Clear visual success/failure indicators
- **Expandable Sections**: Detailed error logs in collapsible sections
- **Actionable Guidance**: Specific commands for local reproduction and fixing
- **Context Information**: Timing, file listings, and diagnostic data

### Artifact Collection
Failure artifacts are automatically collected for offline analysis:
- **Naming Convention**: `{job-name}-failure-logs`
- **Content**: All relevant log files and diagnostic outputs
- **Availability**: Downloadable from GitHub Actions interface

### Local Testing Commands
Each job provides specific commands for local validation:

```bash
# Linting
ruff check .
yamllint .
shellcheck **/*.sh
sqlfluff lint db scripts

# Database validation
python -m scripts.setup_db && pytest

# UI testing
pip install pytest pytest-qt && pytest tests -k "not db"

# Build testing
pip install pyinstaller && pyinstaller --windowed app/main.py
```

## Pipeline Configuration

### Environment Variables
Jobs utilize environment variables for configuration:
- **Database**: `SA_DB_*` variables for MySQL connection
- **Build**: `APP_ENTRY`, `APP_NAME` for build configuration
- **Tool Settings**: Version constraints and execution parameters

### Secrets Management
Secure information stored in GitHub repository secrets:
- `CI_DB_ROOT_PASS`: MySQL root password for test database

### Caching Strategy
Strategic caching improves pipeline performance:
- **Python Dependencies**: pip cache based on `requirements.txt`
- **Lint Baseline**: Tracks first-run vs. incremental linting

## Performance Optimization

### Change Detection
Smart execution based on file changes reduces unnecessary work:
- Only relevant jobs execute based on changed file types
- Incremental linting for faster feedback on small changes
- Conditional job dependencies prevent cascading failures

### Parallel Execution
Jobs execute in parallel where dependencies allow:
- Lint, PlantUML, and Database validation can run concurrently after change detection
- UI validation waits for both lint and database validation
- Both macOS and Windows builds run in parallel after all validation jobs complete

### Resource Management
Efficient resource utilization:
- Cancels in-progress runs when new commits pushed
- Uses appropriate runner types (Ubuntu for testing, macOS/Windows for platform-specific builds)
- Strategic caching reduces setup time

## Maintenance and Extensions

### Adding New Jobs
To add new validation or build jobs:
1. Add change detection patterns in `detect` job filters
2. Create new job with appropriate dependencies
3. Implement error capture and summary generation
4. Add job status to `pipeline-summary`

### Tool Updates
Update tool versions in job installation steps:
- Pin major versions for stability
- Update both installation and documentation simultaneously
- Test updates in feature branches before merging

### Error Handling Improvements
When enhancing error reporting:
- Follow established patterns for output capture
- Add structured logging to summary generation
- Include actionable guidance for common issues
- Maintain artifact collection for debugging

---

## Changelog

### 2025-01-12 - Added Windows Build Support

**Added:**
- New `build-windows` job for Windows application builds
- Windows executable compilation using PyInstaller on windows-latest runner
- Parallel execution of macOS and Windows builds (independent from each other)
- Windows build status integration in pipeline summary
- Windows build artifacts collection (`Windows-build` and `Windows-build-failure-logs`)
- Cross-platform build validation ensuring application works on both major platforms

**Enhanced:**
- Pipeline now supports multi-platform application distribution
- Updated documentation to reflect 8-job pipeline structure
- Improved parallel execution efficiency with independent platform builds

### 2025-09-12 - Enhanced Error Reporting and Job Summaries

**Added:**
- Comprehensive error capture for all linting tools (ruff, yamllint, shellcheck, sqlfluff)
- Detailed job summaries with expandable error sections
- Automatic artifact collection for failed jobs
- Pipeline summary job with overall status table
- Actionable guidance and local testing commands
- Structured output formats (JSON for ruff/sqlfluff, text for others)

**Fixed:**
- Typo: `ppython` → `python` in SQLFluff changed files step
- Broken jq string formatting in SQLFluff summary causing syntax errors
- YAML indentation issues in Python heredoc blocks

**Enhanced:**
- All jobs now provide detailed status breakdowns by component
- Clear success/failure indicators with specific error information
- Downloadable logs for offline debugging and analysis
- Timing information and build artifact listings

**Technical Improvements:**
- Better error propagation while maintaining diagnostic capture
- Environment variable tracking for failure states across job steps
- Conditional execution logic improved for performance
- Standardized summary generation patterns across all jobs