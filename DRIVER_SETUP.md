# MySQL Driver Setup Guide

This document provides instructions for setting up MySQL database drivers for the-studentr application after the migration to PyQt QSql module.

## Overview

The application now uses PyQt's QSql module with a **MySQL-only** approach for simplicity and reliability. This requires MySQL database drivers to be available to PyQt.

## Required Setup

### Native MySQL Driver (QMYSQL) - **Required**

The application requires the Qt5 MySQL driver to be installed on your system.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libqt5sql5-mysql python3-pyqt5 python3-pyqt5.qtsql
```

**CentOS/RHEL:**
```bash
sudo yum install qt5-qtbase-mysql
# or for newer versions:
sudo dnf install qt5-qtbase-mysql
```

**macOS:**
```bash
brew install qt@5
# Note: MySQL support is typically included
```

**Windows:**
- Install Qt5 with MySQL support through the Qt installer
- Or use pre-compiled binaries that include MySQL support

## Python Dependencies

Install the Python packages:

```bash
# Install from requirements.txt (excludes PyQt5 if using system packages)
pip install bcrypt pytest

# For development, you may prefer to install PyQt5 via pip:
pip install PyQt5==5.15.10
# But note: pip-installed PyQt5 may not include system MySQL drivers
```

**Important:** When using pip-installed PyQt5, you may need to install system Qt5 libraries separately. Using system packages (`python3-pyqt5`) is recommended for better driver compatibility.

## Verification

### Check Available Drivers

To see what drivers are available on your system:

```python
from PyQt5.QtSql import QSqlDatabase
print("Available drivers:", QSqlDatabase.drivers())
```

Expected output with MySQL support:
```
Available drivers: ['QSQLITE', 'QMYSQL', 'QMYSQL3', 'QPSQL', ...]
```

You should see `QMYSQL` or `QMYSQL3` in the list.

### Test Database Connection

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your database credentials:**
   ```
   SA_DB_HOST=localhost
   SA_DB_PORT=3306
   SA_DB_USER=your_username
   SA_DB_PASS=your_password
   SA_DB_NAME=the_studentr
   ```

3. **Run the verification script:**
   ```bash
   PYTHONPATH=. python scripts/verify_setup.py
   ```

4. **Run the setup script:**
   ```bash
   PYTHONPATH=. python scripts/setup_db.py
   ```

## Troubleshooting

### Common Error Messages

#### "No MySQL drivers found"
```
❌ No MySQL drivers found
Available drivers: ['QSQLITE', 'QPSQL', ...]
```

**Solution:** Install the Qt5 MySQL driver:
```bash
# Ubuntu/Debian
sudo apt-get install libqt5sql5-mysql python3-pyqt5

# If using pip-installed PyQt5, try switching to system packages
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip
sudo apt-get install python3-pyqt5
```

#### "Access denied for user"
```
Access denied for user 'root'@'localhost' (using password: YES)
```

**Solution:** Check your database credentials in the `.env` file.

#### "Unknown database 'the_studentr'"
```
Unknown database 'the_studentr'
```

**Solution:** Create the database first:
```sql
CREATE DATABASE the_studentr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Docker Environment

If you're using Docker or a containerized environment, make sure to install the MySQL drivers in your container:

```dockerfile
# For Ubuntu-based containers
RUN apt-get update && apt-get install -y \
    libqt5sql5-mysql \
    python3-pyqt5 \
    python3-pyqt5.qtsql
```

### CI/CD Environments

For continuous integration environments (like GitHub Actions), install the system packages:

```yaml
- name: Install Qt5 MySQL dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libqt5sql5-mysql python3-pyqt5 python3-pyqt5.qtsql
```

## Migration Notes

If you're upgrading from the MySQLdb version:

1. The API remains the same - no code changes required
2. Parameter placeholders changed from `%s` to `?` (handled automatically)
3. Error handling maintains MySQLdb compatibility
4. Connection management is now handled by PyQt
5. **Simplified:** Only MySQL is supported (no ODBC/SQLite fallbacks)

## Support

If you encounter issues:

1. Check that PyQt5 is properly installed (preferably system packages)
2. Verify MySQL drivers are available using the verification steps above
3. Ensure MySQL server is running and accessible
4. Check the application logs for detailed error messages

For more information, see the [MIGRATION_NOTES.md](MIGRATION_NOTES.md) file.