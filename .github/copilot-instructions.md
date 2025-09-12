# the-studentr - Student Assignment & Grade Manager

Python-based desktop application built with PyQt5 and MySQL for managing student assignments, due dates, and grade calculations. The application provides a local-user-only student assistant tool with assignment tracking and grade book functionality.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Environment Setup & Dependencies

### Required System Dependencies
Install the following system packages before building:
```bash
sudo apt-get update
sudo apt-get install -y libmysqlclient-dev mysql-server mysql-client
```

### Python Environment
- **Python Version**: 3.11+ (tested with 3.12)
- **Package Manager**: pip

Install Python dependencies:
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### MySQL Database Setup
The application requires a MySQL database. Use Docker for consistent setup:

```bash
# Start MySQL container (NEVER CANCEL - takes 1-2 minutes for first pull)
docker run --name mysql-test -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=the_studentr -p 3306:3306 -d mysql:9.0

# Wait for MySQL to be ready (NEVER CANCEL - takes 10-30 seconds)
sleep 15
docker exec mysql-test mysqladmin ping -h 127.0.0.1 -prootpass
```

## Configuration

### Environment Variables
Set these environment variables or create a `.env` file:
```bash
SA_DB_HOST=127.0.0.1
SA_DB_PORT=3306
SA_DB_USER=root
SA_DB_PASS=rootpass
SA_DB_NAME=the_studentr
```

### .env File Setup
Create a `.env` file with your database credentials:
```bash
cat > .env << 'EOF'
SA_DB_HOST=127.0.0.1
SA_DB_PORT=3306
SA_DB_USER=root
SA_DB_PASS=rootpass
SA_DB_NAME=the_studentr
EOF
```

**Note**: The `.env.example` file contains placeholder values and must be customized.

## Database Initialization

### Initial Setup (NEVER CANCEL - takes 30-60 seconds)
```bash
export PYTHONPATH=$PWD
python -m scripts.setup_db
```

### Verify Database Connection
```bash
export PYTHONPATH=$PWD
python -m scripts.dal_smoke
```

## Running the Application

### GUI Application
```bash
# Set Python path for module imports
export PYTHONPATH=$PWD

# Run the desktop application
python app/main.py
```

**Note**: The GUI application is currently a minimal PyQt5 window. Full application features are in development.

### Development Scripts
```bash
# Database setup
python -m scripts.setup_db

# DAL connectivity test
python -m scripts.dal_smoke

# CI smoke test (comprehensive validation)
python -m scripts.ci_smoke
```

## Testing & Validation

### Run Unit Tests (NEVER CANCEL - takes 5-10 seconds)
```bash
export PYTHONPATH=$PWD
pytest -q
```

### Full Test Suite with Timing
```bash
export PYTHONPATH=$PWD
time pytest -q
# Expected: ~3-4 seconds for all tests
```

## Linting & Code Quality

### Install Linting Tools
```bash
pip install ruff==0.6.*
sudo apt-get install -y yamllint shellcheck
pip install "sqlfluff==3.*"
```

### Run All Linters (NEVER CANCEL - takes 5-15 seconds total)
```bash
# Python linting (~0.01 seconds)
ruff check .

# Fix auto-fixable Python issues
ruff check . --fix

# YAML linting (~0.4 seconds)  
yamllint -s .

# Shell script linting (if any .sh files exist)
find . -name "*.sh" -exec shellcheck {} \;

# SQL linting (~1 second, may show style violations)
sqlfluff lint db scripts --dialect mysql --format json --write-output sqlfluff.json
```

**Note**: SQLFluff may report style violations. These are not blocking unless explicitly configured to fail the build.

## Building & Distribution

### Install Build Tools
```bash
pip install pyinstaller==6.6.*
```

### Build Standalone Application (NEVER CANCEL - takes 5-10 minutes)
```bash
# Create application bundle - SET TIMEOUT TO 15+ MINUTES
mkdir -p dist
time pyinstaller --noconfirm --windowed --name "the-studentr" app/main.py

# Verify build output
ls -la dist/the-studentr/
```

**Build Time**: Expect 7-8 seconds on fast systems, up to 10 minutes on slower systems.

### Test Built Application
```bash
# Run built application (requires X11/display)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
./dist/the-studentr/the-studentr
```

## Validation Scenarios

### Complete Development Workflow
Always run this complete sequence when making changes:

1. **Environment Setup** (first time only):
   ```bash
   sudo apt-get install -y libmysqlclient-dev mysql-server mysql-client
   pip install -r requirements.txt
   docker run --name mysql-test -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=the_studentr -p 3306:3306 -d mysql:9.0
   sleep 15
   ```

2. **Database Setup**:
   ```bash
   export PYTHONPATH=$PWD
   python -m scripts.setup_db
   python -m scripts.dal_smoke
   ```

3. **Code Quality Checks**:
   ```bash
   ruff check .
   ruff check . --fix  # Fix auto-fixable issues
   yamllint -s .
   sqlfluff lint db scripts --dialect mysql
   ```

4. **Testing**:
   ```bash
   export PYTHONPATH=$PWD
   pytest -q
   python -m scripts.ci_smoke
   ```

5. **Application Testing**:
   ```bash
   python app/main.py  # Manual verification of GUI startup
   ```

6. **Build Verification** (if needed):
   ```bash
   pyinstaller --noconfirm --windowed --name "the-studentr" app/main.py
   ```

### CI Pipeline Simulation
To replicate the GitHub Actions pipeline locally:
```bash
# Follow the complete development workflow above
# All steps should pass without errors
# SQLFluff may show style violations (non-blocking)
```

## Project Structure

### Key Directories
- `app/` - Application source code
  - `dal/` - Data Access Layer (database operations)
  - `config/` - Configuration management
  - `main.py` - GUI application entry point
- `db/` - Database schema and seed data
  - `schema.sql` - Database table definitions
  - `seed.sql` - Initial data
- `scripts/` - Setup and maintenance scripts
- `tests/` - Unit tests
- `docs/` - Documentation and diagrams

### Important Files
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `.github/workflows/pipeline.yml` - CI/CD configuration
- `.sqlfluff.ini` - SQL linting configuration

## Common Issues & Solutions

### MySQL Connection Issues
```bash
# Check MySQL container status
docker ps
docker logs mysql-test

# Restart MySQL container
docker stop mysql-test && docker rm mysql-test
docker run --name mysql-test -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=the_studentr -p 3306:3306 -d mysql:9.0
```

### Python Module Import Issues
```bash
# Always set PYTHONPATH for script execution
export PYTHONPATH=$PWD
```

### PyQt5 GUI Issues
```bash
# For headless environments, set up virtual display
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
```

### Build Issues
```bash
# Clean build artifacts and retry
rm -rf build/ dist/ *.spec
pyinstaller --noconfirm --windowed --name "the-studentr" app/main.py
```

## Timeout Recommendations

**CRITICAL - NEVER CANCEL these operations before the specified timeouts:**

- **MySQL container startup**: 2-3 minutes (first time pull)
- **Database setup script**: 1-2 minutes  
- **PyInstaller build**: 10-15 minutes (set timeout to 20+ minutes)
- **Unit tests**: 30 seconds
- **Linting (all tools)**: 1-2 minutes
- **SQLFluff**: 2-3 minutes for full repo

## Development Notes

- The application is designed for local single-user deployment
- Database uses MySQL with parameterized queries for security
- PyQt5 is used for cross-platform desktop GUI
- Build artifacts are created in `dist/` directory
- All database operations require user scoping for future multi-user support
- The project supports both environment variables and `.env` file configuration