# CI Pipeline Enhancements

This document describes the improvements made to the CI pipeline in `.github/workflows/pipeline.yml` to provide better error reporting and job summaries.

## Key Improvements

### 1. Enhanced Error Capture
All jobs now capture detailed error information when failures occur:

- **Lint Job**: Captures output from ruff, yamllint, shellcheck, and sqlfluff
- **Database Validation**: Logs from database setup, DAL smoke tests, and pytest
- **UI/Logic Validation**: Detailed test failure logs
- **Build Job**: PyInstaller and DMG creation diagnostics

### 2. Comprehensive Job Summaries
Each job provides detailed status information:

```markdown
## Lint Results: **failed**

### 🐍 Python (Ruff)
**Status:** ❌ Failed

<details><summary>Ruff violations</summary>

```json
[{"type": "error", "code": "F401", "message": "unused import"}]
```

</details>

### 📄 YAML (yamllint)
**Status:** ✅ Passed

### Next steps:
1. Review the specific violations in each section
2. Fix the issues locally
3. Re-run the linters locally
4. Commit and push your fixes
```

### 3. Failure Artifacts
When jobs fail, relevant logs are automatically uploaded as artifacts:

- `lint-failure-logs`: All linting tool outputs
- `db-validation-failure-logs`: Database and test logs  
- `ui-validation-failure-logs`: UI test outputs
- `macOS-build-failure-logs`: Build error logs

### 4. Pipeline Summary
A new `pipeline-summary` job provides an overall status table:

| Job | Status | Notes |
|-----|--------|-------|
| 🔍 Change Detection | ✅ Success | Changes detected and analyzed |
| 🧹 Lint | ❌ Failed | Code quality issues found |
| 🗄️ Database Validation | ✅ Success | All DB tests passed |
| 🖥️ UI/Logic Validation | ⏭️ Skipped | No UI changes |
| 🍎 macOS Build | ✅ Success | Application built successfully |

## Benefits for Developers

### Before
- Basic "job failed" message
- No error context
- Manual investigation required
- Time-consuming debugging

### After  
- Detailed error breakdown by tool
- Specific file and line information
- Actionable next steps
- Downloadable logs for offline analysis
- Clear guidance on local testing commands

## Usage

The enhanced pipeline automatically provides detailed summaries for all runs. No additional configuration is required.

### For Failed Jobs:
1. Check the job summary for detailed error breakdown
2. Download failure artifacts if needed
3. Follow the "Next steps" guidance
4. Test fixes locally using provided commands
5. Re-run pipeline after fixes

### Available Local Commands:
```bash
# Linting
ruff check .
yamllint .
shellcheck **/*.sh
sqlfluff lint db scripts

# Database tests
python -m scripts.setup_db && pytest

# UI tests  
pip install pytest pytest-qt && pytest tests -k "not db"

# Build test
pip install pyinstaller && pyinstaller --windowed app/main.py
```

## Error Examples

The pipeline now provides specific guidance for common issues:

- **Import errors**: Shows exact unused imports with file locations
- **YAML formatting**: Highlights specific line and column issues
- **Database connectivity**: Provides MySQL connection diagnostics
- **Build failures**: Shows missing dependencies and module issues
- **Test failures**: Displays full test output with stack traces

This makes the CI pipeline significantly more helpful for development and debugging.