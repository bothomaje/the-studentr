# GitHub Copilot Instructions for the-studentr Repository

## Project Overview

**the-studentr** is a desktop Student Assistant application built with Python, PyQt5, and MySQL. It provides assignment tracking with due-date management and a grade book for calculating academic marks with color-coded status indicators.

### Key Components
- **Login System**: Fixed username/password authentication
- **Dashboard**: Calendar, clock, and assignment overview widgets  
- **Assignment Tracker**: CRUD operations with due date calculations
- **Grade Management**: Module-based assessment tracking with weighted calculations

## Architecture & Code Organization

### Directory Structure
```
app/
├── config/          # Configuration management
│   ├── env.py      # Environment variable loading
│   └── __init__.py
├── dal/            # Data Access Layer
│   ├── base.py     # Database connection utilities
│   ├── users_dal.py      # User management
│   ├── modules_dal.py    # Academic modules
│   ├── assignments_dal.py # Assignment CRUD
│   ├── marks_dal.py      # Grade calculations
│   └── __init__.py
└── __init__.py

db/                 # Database schemas and setup files
docs/               # Project documentation
tests/              # Unit tests for DAL components
scripts/            # Setup and utility scripts
```

### Database Schema
- **modules**: Academic modules with grading rules
- **assignments**: Assignment tracking with dates and status
- **marks**: Assessment weights and scores
- **views**: Pre-computed aggregations for dashboard

## Development Patterns & Conventions

### Data Access Layer (DAL) Patterns

When working with database operations, follow these established patterns:

#### 1. Connection Management
```python
from app.dal.base import db_conn, db_cursor, transaction

# Standard query pattern
with db_conn() as conn:
    with db_cursor(conn) as cur:
        cur.execute("SELECT * FROM modules WHERE id = %s", (module_id,))
        return cur.fetchone()

# Transaction pattern for multiple operations
with db_conn() as conn:
    with transaction(conn):
        # Multiple related operations here
        pass
```

#### 2. Parameterized Queries
Always use parameterized queries to prevent SQL injection:
```python
# ✅ Correct - parameterized
cur.execute("SELECT * FROM assignments WHERE module_id = %s", (module_id,))

# ❌ Incorrect - string formatting
cur.execute(f"SELECT * FROM assignments WHERE module_id = {module_id}")
```

#### 3. Error Handling
Use the custom exception classes and handle MySQL errors appropriately:
```python
from app.dal.base import NotFoundError, ForbiddenError
import MySQLdb

def create_assignment(...):
    try:
        # Insert logic here...
    except MySQLdb.IntegrityError as e:
        if getattr(e, "args", None) and e.args[0] in (1452,):
            raise ValueError("Invalid module_id (FK)") from e
        raise

def get_assignment(assignment_id: str, user_id: str) -> Optional[dict]:
    # Query logic here...
    # Returns None if not found rather than raising exception
    return fetch_one(conn, sql, (assignment_id, user_id))
```

### Configuration Management

Environment variables are loaded via `app.config.env.load_env()`:
```python
# Database configuration
SA_DB_HOST=localhost
SA_DB_PORT=3306
SA_DB_USER=root
SA_DB_PASS=your_password
SA_DB_NAME=the_studentr
```

Access config through `config_from_env()`:
```python
from app.dal.base import config_from_env
config = config_from_env()
```

### Type Hints & Modern Python

This codebase uses modern Python features:
- **Type hints**: Use `from __future__ import annotations` for forward references
- **Dataclasses**: Use `@dataclass(frozen=True)` for immutable data structures
- **Context managers**: Leverage `@contextmanager` for resource management
- **Optional types**: Use `Optional[T]` for nullable values

Example:
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Assignment:
    id: int
    module_id: int
    title: str
    due_date: str
    status: str
    submit_date: Optional[str] = None
```

## Business Logic & Domain Rules

### Assignment Status Management
Valid statuses: `'Not Started'`, `'In Progress'`, `'Done'`, `'Skipped'`

Assignment types by category:
- **Formative**: Quiz, Written assignment, Practical  
- **Exam**: Quiz, Written exam, Take-Home exam

### Assignment IDs and Module IDs
- Use `str(uuid.uuid4())` for generating assignment IDs
- All IDs are string-based, not integers

### Grade Calculation Rules
1. **Year Mark**: Weighted average of formative assessments
2. **Final Mark**: `(Year Mark × Year Weight) + (Exam Mark × Exam Weight)`
3. **Pass Threshold**: Final mark ≥ 50%
4. **Exam Subminimum**: Module-specific minimum exam score requirement

### Color-Coded Status Logic
- **Yellow**: Submission not completed
- **Orange**: Submitted but not yet scored  
- **Green**: Score ≥ 50% and all requirements met
- **Red**: Score < 50% OR subminimum not met OR exam entry criteria failed

### Date Calculations
Use `DATEDIFF(due_date, CURDATE())` for "days remaining" calculations in SQL queries.

## GUI Development with PyQt5

### Widget Organization
- Use `QStackedWidget` for navigation between main pages
- Implement signal/slot connections for user interactions
- Use appropriate input widgets: `QDateEdit` for dates, `QSpinBox` for numeric values

### Validation Patterns
Always validate inputs using the DAL's built-in validation functions:

```python
from app.dal.assignments_dal import _validate_submit_status, _validate_category_type
from app.dal.marks_dal import _validate_weight, _validate_score

# Validate assignment status
_validate_submit_status("Done")  # OK
_validate_submit_status("Invalid")  # Raises ValueError

# Validate category and assignment type combination  
_validate_category_type("Formative", "Quiz")  # OK
_validate_category_type("Formative", "Written exam")  # Raises ValueError

# Validate marks (0-100 range)
_validate_weight(75.0)  # OK
_validate_score(85.5)   # OK
_validate_weight(150.0) # Raises ValueError
```

### GUI Input Validation
- Validate dates, weights (0-100%), scores (0-100%) at input time
- Provide immediate feedback for validation errors
- Warn if assessment weights for a module don't sum to 100%

### Dashboard Widgets
- **Calendar**: Show current date and highlight important dates
- **Clock**: Live updating time display
- **Status Panels**: Upcoming assignments and quick status counts

## Testing Guidelines

### Test Structure
Tests are organized by DAL component:
- `test_users_dal.py`
- `test_modules_dal.py` 
- `test_assignments_dal.py`
- `test_marks_dal.py`

### Test Database Setup
Use `conftest.py` for shared test fixtures and database setup.

### Testing Patterns
```python
import datetime as dt
from app.dal import users_dal, modules_dal, assignments_dal, marks_dal

def test_assignment_flow(db_conn, db_tx):
    # Create test user and module
    uid = users_dal.create_user(
        username="testuser", 
        email="test@example.com", 
        password="A1b2C3d4!", 
        first_name="Test", 
        surname="User"
    )
    mod_id = modules_dal.create_module(
        user_id=uid, 
        module_code="TEST101",
        module_name="Test Module", 
        year_mark_weight=50, 
        exam_weight=50,
        min_assignments=1
    )
    
    # Create assignment
    a_id = assignments_dal.create_assignment(
        module_id=mod_id,
        assignment_title="Test Assignment",
        category="Formative",
        assignment_type="Quiz",
        due_date=dt.date.today(),
        submit_status="Not Started",
        user_id=uid
    )
    
    # Test mark operations
    marks_dal.insert_mark(assignment_id=a_id, weight=10, score=None)
    assignments_dal.update_submit_status(a_id, "Done")
    marks_dal.update_mark_score(assignment_id=a_id, score=76)
    
    # Verify results
    upcoming = assignments_dal.list_upcoming_for_user(user_id=uid, days=30)
    assert isinstance(upcoming, list)
```

## Common Development Tasks

### Adding a New Database Table
1. Create migration script in `db/` directory
2. Add corresponding DAL module in `app/dal/`
3. Implement CRUD operations following existing patterns
4. Add comprehensive tests
5. Update views if dashboard integration needed

### Implementing New Business Rules
1. Document the rule in business logic section
2. Implement in appropriate DAL module
3. Add validation logic
4. Create unit tests covering edge cases
5. Update GUI to reflect new behavior

### Adding New GUI Features
1. Design with Qt Designer or create programmatically
2. Follow existing navigation patterns
3. Implement proper validation
4. Connect signals/slots appropriately
5. Test with various data scenarios

## Dependencies & Environment

### Required Python Packages
- `mysqlclient~=2.2` - MySQL database connectivity
- `PyQt5~=5.15.10` - GUI framework
- `bcrypt~=4.1` - Password hashing (if implementing user auth)
- `pytest~=7.4.4` - Testing framework

### Development Setup
1. Install MySQL and create database
2. Load schema from `db/` directory  
3. Configure `.env` file with database credentials
4. Install Python dependencies: `pip install -r requirements.txt`
5. Run tests to verify setup: `python -m pytest`

## Code Quality Standards

### SQL Guidelines
- Use `.sqlfluff.ini` configuration for SQL formatting
- Write readable, well-formatted queries
- Prefer views for complex aggregations used in multiple places

### Python Standards  
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Document complex business logic with comments
- Keep functions focused and single-purpose

### Error Handling
- Handle database connection errors gracefully
- Provide meaningful error messages to users
- Log errors appropriately for debugging
- Never expose internal implementation details in user-facing errors

## Performance Considerations

- Dataset expected to be small (single student)
- All pages should load under 200ms
- Use database views for dashboard aggregations
- Consider caching for frequently accessed data
- Optimize queries with appropriate indexes

## Security Best Practices

- Always use parameterized queries
- Validate all user inputs
- Store sensitive configuration in environment variables
- Handle authentication securely (if implementing multi-user features)
- Regular backup of student data

This codebase emphasizes clean architecture, type safety, and robust error handling. When extending functionality, maintain consistency with existing patterns and always include comprehensive tests.