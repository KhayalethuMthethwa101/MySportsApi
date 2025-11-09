# Database Query Guide

This guide shows you how to query your PostgreSQL database tables using terminal commands.

## Database Connection

### Connect to PostgreSQL Database
```bash
# Connect to the database container
docker exec -it sports_api_postgres psql -U sports_user -d sports_db

# Alternative: Connect through Docker Compose
docker-compose exec db psql -U sports_user -d sports_db
```

### Connection Details
- **Host**: localhost (from host machine) or `db` (from within Docker network)
- **Port**: 5432
- **Database**: sports_db
- **Username**: sports_user
- **Password**: sports_pass_2024 (from .env file)

## Basic PostgreSQL Commands

### Database Information
```sql
-- List all databases
\l

-- Connect to a specific database
\c sports_db

-- Show current database
SELECT current_database();

-- Show current user
SELECT current_user;

-- Quit psql
\q
```

### Table Information
```sql
-- List all tables
\dt

-- List all tables with more details
\dt+

-- Describe a specific table structure
\d table_name

-- Show table with column details
\d+ table_name

-- List all schemas
\dn

-- Show table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'your_table_name';
```

## Django Tables

### Common Django System Tables
```sql
-- List Django migrations
SELECT * FROM django_migrations;

-- List Django admin log entries
SELECT * FROM django_admin_log ORDER BY action_time DESC LIMIT 10;

-- List Django users
SELECT id, username, email, is_staff, is_superuser, date_joined 
FROM auth_user;

-- List Django sessions
SELECT * FROM django_session;

-- List Django content types
SELECT * FROM django_content_type;
```

## Premier League Service Tables

### Basic Queries
```sql
-- Show all tables related to premier league service
\dt *premier*

-- If you have custom models, query them:
-- (Replace with your actual table names)

-- Example: Teams table (if exists)
SELECT * FROM premier_league_service_team LIMIT 10;

-- Example: Players table (if exists)
SELECT * FROM premier_league_service_player LIMIT 10;

-- Example: Matches table (if exists)
SELECT * FROM premier_league_service_match LIMIT 10;
```

### Advanced Queries
```sql
-- Count records in a table
SELECT COUNT(*) FROM table_name;

-- Get table structure with constraints
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'your_table_name';

-- Show foreign key relationships
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name='your_table_name';
```

## Data Analysis Queries

### Sample Data Analysis
```sql
-- Get record counts for all tables
SELECT 
    schemaname,
    tablename,
    n_tup_ins as "Total Inserts",
    n_tup_upd as "Total Updates",
    n_tup_del as "Total Deletes",
    n_live_tup as "Live Rows",
    n_dead_tup as "Dead Rows"
FROM pg_stat_user_tables 
ORDER BY n_live_tup DESC;

-- Database size information
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE pg_database.datname = 'sports_db';

-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size,
    pg_size_pretty(pg_relation_size(tablename::regclass)) as table_size,
    pg_size_pretty(pg_total_relation_size(tablename::regclass) - pg_relation_size(tablename::regclass)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

## Quick Terminal Commands

### One-liner Database Queries
```bash
# Count records in auth_user table
docker exec -it sports_api_postgres psql -U sports_user -d sports_db -c "SELECT COUNT(*) FROM auth_user;"

# List all table names
docker exec -it sports_api_postgres psql -U sports_user -d sports_db -c "\dt"

# Show database size
docker exec -it sports_api_postgres psql -U sports_user -d sports_db -c "SELECT pg_size_pretty(pg_database_size('sports_db'));"

# Export query results to CSV
docker exec -it sports_api_postgres psql -U sports_user -d sports_db -c "\copy (SELECT * FROM auth_user) TO '/tmp/users.csv' CSV HEADER"

# Import CSV data
docker exec -it sports_api_postgres psql -U sports_user -d sports_db -c "\copy table_name FROM '/tmp/data.csv' DELIMITER ',' CSV HEADER"
```

## Backup and Restore

### Database Backup
```bash
# Create a backup
docker exec -it sports_api_postgres pg_dump -U sports_user -d sports_db > backup.sql

# Create a compressed backup
docker exec -it sports_api_postgres pg_dump -U sports_user -d sports_db | gzip > backup.sql.gz

# Backup specific tables
docker exec -it sports_api_postgres pg_dump -U sports_user -d sports_db -t table_name > table_backup.sql
```

### Database Restore
```bash
# Restore from backup
cat backup.sql | docker exec -i sports_api_postgres psql -U sports_user -d sports_db

# Restore compressed backup
gunzip -c backup.sql.gz | docker exec -i sports_api_postgres psql -U sports_user -d sports_db
```

## Monitoring and Performance

### Active Connections
```sql
-- Show active connections
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity 
WHERE state != 'idle';

-- Kill a specific connection
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = 'process_id';
```

### Query Performance
```sql
-- Show slow queries (if pg_stat_statements is enabled)
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- Show table statistics
SELECT * FROM pg_stat_user_tables WHERE relname = 'your_table_name';
```

## Useful Shortcuts

### psql Command Shortcuts
```
\?          # Help with psql commands
\h          # Help with SQL commands
\l          # List databases
\dt         # List tables
\du         # List users
\dp         # List permissions
\timing     # Toggle timing of commands
\x          # Toggle expanded display
\g          # Execute last command
\s          # Show command history
\i file     # Execute commands from file
\o file     # Redirect output to file
```

### Environment Variables for Quick Access
Add to your shell profile (.bashrc, .zshrc, etc.):
```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=sports_db
export PGUSER=sports_user
export PGPASSWORD=sports_pass_2024

# Then you can simply run:
# psql (connects automatically with above settings)
```

## Troubleshooting

### Common Issues
```bash
# Check if database is running
docker ps | grep postgres

# Check database logs
docker logs sports_api_postgres

# Check connection
docker exec -it sports_api_postgres pg_isready -U sports_user -d sports_db

# Reset database connection
docker-compose restart db

# Access database from host machine (if port is exposed)
psql -h localhost -p 5432 -U sports_user -d sports_db
```

### Django-specific Queries
```bash
# Check Django migrations status
docker exec -it sports_api_web python manage.py showmigrations

# Apply pending migrations
docker exec -it sports_api_web python manage.py migrate

# Create database shell (Django ORM)
docker exec -it sports_api_web python manage.py dbshell
```

## Security Notes

- Never log sensitive queries in production
- Always use parameterized queries for user input
- Regularly backup your database
- Monitor for unusual query patterns
- Use read-only users for reporting queries
- Consider using connection pooling for high-traffic applications

## Quick Reference Card

```
Connection:     docker exec -it sports_api_postgres psql -U sports_user -d sports_db
List tables:    \dt
Table info:     \d table_name
Quit:          \q
Count rows:    SELECT COUNT(*) FROM table_name;
Recent data:   SELECT * FROM table_name ORDER BY id DESC LIMIT 10;
```