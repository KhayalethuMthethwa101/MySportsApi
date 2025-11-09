#!/bin/bash

# Database Query Helper Script
# Usage: ./db-helper.sh [command]

DB_CONTAINER="sports_api_postgres"
DB_USER="sports_user"
DB_NAME="sports_db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to execute SQL command
execute_sql() {
    docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "$1"
}

# Function to show help
show_help() {
    echo -e "${BLUE}Database Query Helper${NC}"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  tables          - List all tables"
    echo "  size           - Show database and table sizes"
    echo "  users          - List Django users"
    echo "  migrations     - Show Django migrations"
    echo "  stats          - Show table statistics"
    echo "  connect        - Connect to database shell"
    echo "  backup         - Create database backup"
    echo "  logs           - Show database logs"
    echo "  status         - Check database status"
    echo ""
    echo "Examples:"
    echo "  $0 tables"
    echo "  $0 users"
    echo "  $0 connect"
}

case "$1" in
    "tables")
        echo -e "${GREEN}All Tables:${NC}"
        execute_sql "\dt"
        ;;
    "size")
        echo -e "${GREEN}Database Size:${NC}"
        execute_sql "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));"
        echo -e "${GREEN}Table Sizes:${NC}"
        execute_sql "SELECT 
            tablename,
            pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(tablename::regclass) DESC;"
        ;;
    "users")
        echo -e "${GREEN}Django Users:${NC}"
        execute_sql "SELECT id, username, email, is_staff, is_superuser, date_joined FROM auth_user ORDER BY date_joined DESC;"
        ;;
    "migrations")
        echo -e "${GREEN}Django Migrations:${NC}"
        execute_sql "SELECT app, name, applied FROM django_migrations ORDER BY applied DESC LIMIT 10;"
        ;;
    "stats")
        echo -e "${GREEN}Table Statistics:${NC}"
        execute_sql "SELECT 
            schemaname,
            tablename,
            n_live_tup as \"Live Rows\",
            n_dead_tup as \"Dead Rows\",
            last_vacuum,
            last_analyze
        FROM pg_stat_user_tables 
        ORDER BY n_live_tup DESC;"
        ;;
    "connect")
        echo -e "${GREEN}Connecting to database...${NC}"
        docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
        ;;
    "backup")
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        echo -e "${GREEN}Creating backup: $BACKUP_FILE${NC}"
        docker exec -it $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILE
        echo -e "${GREEN}Backup completed: $BACKUP_FILE${NC}"
        ;;
    "logs")
        echo -e "${GREEN}Database Logs:${NC}"
        docker logs $DB_CONTAINER --tail 50
        ;;
    "status")
        echo -e "${GREEN}Database Status:${NC}"
        docker ps | grep $DB_CONTAINER
        echo ""
        echo -e "${GREEN}Connection Test:${NC}"
        docker exec -it $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac