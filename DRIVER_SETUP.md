# MySQL Driver Setup Guide

This document provides instructions for setting up MySQL database drivers for the-studentr application after the migration to PyQt QSql module.

## Overview

The application now uses PyQt's QSql module instead of MySQLdb. This requires MySQL database drivers to be available to PyQt. The application will automatically detect and use the best available driver.

## Driver Options (in order of preference)

### 1. Native MySQL Driver (QMYSQL) - **Recommended**

This is the preferred option as it provides the best performance and compatibility.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libqt5sql5-mysql
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

### 2. MySQL ODBC Driver (QODBC) - **Alternative**

If the native driver is not available, the application can use ODBC as a fallback.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libmyodbc
```

**CentOS/RHEL:**
```bash
sudo yum install mysql-connector-odbc
# or for newer versions:
sudo dnf install mysql-connector-odbc
```

**macOS:**
```bash
brew install mysql-connector-odbc
```

**Windows:**
- Download MySQL Connector/ODBC from the MySQL website
- Install the appropriate version (8.0 recommended)

### 3. SQLite Testing Mode - **Development Only**

For testing and development purposes, you can use SQLite instead of MySQL:

```bash
python scripts/setup_db.py --sqlite
```

**Note:** This creates a simplified database structure and some features may not work as expected.

## Verification

### Check Available Drivers

To see what drivers are available on your system:

```python
from PyQt5.QtSql import QSqlDatabase
print("Available drivers:", QSqlDatabase.drivers())
```

Expected output with MySQL support:
```
Available drivers: ['QSQLITE', 'QODBC', 'QODBC3', 'QMYSQL', 'QPSQL', 'QPSQL7']
```

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

3. **Run the setup script:**
   ```bash
   PYTHONPATH=. python scripts/setup_db.py
   ```

## Troubleshooting

### Common Error Messages

#### "No MySQL drivers found"
```
✗ No MySQL drivers found
Available Qt SQL drivers: ['QSQLITE', 'QODBC', 'QODBC3', 'QPSQL', 'QPSQL7']
```

**Solution:** Install the native MySQL driver (libqt5sql5-mysql) or MySQL ODBC driver.

#### "Can't open lib 'MySQL ODBC 8.0 Unicode Driver'"
```
[unixODBC][Driver Manager]Can't open lib 'MySQL ODBC 8.0 Unicode Driver' : file not found
```

**Solution:** Install the MySQL ODBC driver package (libmyodbc).

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
RUN apt-get update && apt-get install -y libqt5sql5-mysql

# Alternative: ODBC driver
RUN apt-get update && apt-get install -y libmyodbc
```

### CI/CD Environments

For continuous integration environments, you might want to use the SQLite testing mode:

```bash
# In your CI script
PYTHONPATH=. python scripts/setup_db.py --sqlite
```

## Migration Notes

If you're upgrading from the MySQLdb version:

1. The API remains the same - no code changes required
2. Parameter placeholders changed from `%s` to `?` (handled automatically)
3. Error handling maintains MySQLdb compatibility
4. Connection management is now handled by PyQt

## Support

If you encounter issues:

1. Check that PyQt5 is properly installed: `pip install PyQt5==5.15.10`
2. Verify MySQL drivers are available using the verification steps above
3. Try the SQLite testing mode for development: `--sqlite`
4. Check the application logs for detailed error messages

For more information, see the [MIGRATION_NOTES.md](MIGRATION_NOTES.md) file.