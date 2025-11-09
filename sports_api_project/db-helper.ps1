# Database Query Helper Script for PowerShell
# Usage: .\db-helper.ps1 [command]

param(
    [string]$Command = "help"
)

$DB_CONTAINER = "sports_api_postgres"
$DB_USER = "sports_user"
$DB_NAME = "sports_db"

# Function to execute SQL command
function Execute-SQL {
    param([string]$Query)
    docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c $Query
}

# Function to show help
function Show-Help {
    Write-Host "Database Query Helper" -ForegroundColor Blue
    Write-Host "Usage: .\db-helper.ps1 [command]"
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  tables          - List all tables"
    Write-Host "  size           - Show database and table sizes"
    Write-Host "  users          - List Django users"
    Write-Host "  migrations     - Show Django migrations"
    Write-Host "  stats          - Show table statistics"
    Write-Host "  connect        - Connect to database shell"
    Write-Host "  backup         - Create database backup"
    Write-Host "  logs           - Show database logs"
    Write-Host "  status         - Check database status"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\db-helper.ps1 tables"
    Write-Host "  .\db-helper.ps1 users"
    Write-Host "  .\db-helper.ps1 connect"
}

switch ($Command.ToLower()) {
    "tables" {
        Write-Host "All Tables:" -ForegroundColor Green
        Execute-SQL "\dt"
    }
    "size" {
        Write-Host "Database Size:" -ForegroundColor Green
        Execute-SQL "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));"
        Write-Host "Table Sizes:" -ForegroundColor Green
        Execute-SQL "SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(tablename::regclass) DESC;"
    }
    "users" {
        Write-Host "Django Users:" -ForegroundColor Green
        Execute-SQL "SELECT id, username, email, is_staff, is_superuser, date_joined FROM auth_user ORDER BY date_joined DESC;"
    }
    "migrations" {
        Write-Host "Django Migrations:" -ForegroundColor Green
        Execute-SQL "SELECT app, name, applied FROM django_migrations ORDER BY applied DESC LIMIT 10;"
    }
    "stats" {
        Write-Host "Table Statistics:" -ForegroundColor Green
        Execute-SQL "SELECT schemaname, tablename, n_live_tup as \`"Live Rows\`", n_dead_tup as \`"Dead Rows\`", last_vacuum, last_analyze FROM pg_stat_user_tables ORDER BY n_live_tup DESC;"
    }
    "connect" {
        Write-Host "Connecting to database..." -ForegroundColor Green
        docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
    }
    "backup" {
        $BackupFile = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
        Write-Host "Creating backup: $BackupFile" -ForegroundColor Green
        docker exec -it $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > $BackupFile
        Write-Host "Backup completed: $BackupFile" -ForegroundColor Green
    }
    "logs" {
        Write-Host "Database Logs:" -ForegroundColor Green
        docker logs $DB_CONTAINER --tail 50
    }
    "status" {
        Write-Host "Database Status:" -ForegroundColor Green
        docker ps | Select-String $DB_CONTAINER
        Write-Host ""
        Write-Host "Connection Test:" -ForegroundColor Green
        docker exec -it $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME
    }
    default {
        if ($Command -ne "help") {
            Write-Host "Unknown command: $Command" -ForegroundColor Red
            Write-Host ""
        }
        Show-Help
    }
}