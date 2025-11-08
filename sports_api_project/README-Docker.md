# Sports API Docker Management

## Quick Start Commands

### Build and Start
```powershell
docker-compose up --build -d
```

### Stop Services
```powershell
docker-compose down
```

### Stop and Remove Volumes (Fresh Start)
```powershell
docker-compose down -v
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Web service only
docker logs sports_api_web -f

# Database only
docker logs sports_api_postgres -f
```

### Django Management Commands
```powershell
# Run migrations
docker exec -it sports_api_web python manage.py migrate

# Create superuser
docker exec -it sports_api_web python manage.py createsuperuser

# Django shell
docker exec -it sports_api_web python manage.py shell

# Collect static files
docker exec -it sports_api_web python manage.py collectstatic

# Check deployment readiness (security settings)
docker exec -it sports_api_web python manage.py check --deploy
```

### Database Access
```powershell
# Connect to PostgreSQL
docker exec -it sports_api_postgres psql -U sports_user -d sports_db

# List tables
docker exec -it sports_api_postgres psql -U sports_user -d sports_db -c "\dt"
```

## Service URLs
- **Web Application**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **Database**: localhost:5432

## Environment Setup

### First Time Setup
1. Copy the environment template:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` file with your configuration:
   - Update database credentials
   - Generate a new SECRET_KEY
   - Configure other settings as needed

### Default Credentials (Development Only)
- **Database**: Configured in `.env` file
- **Django Admin**: Create with `docker exec -it sports_api_web python manage.py createsuperuser`

⚠️ **Security Note**: Never use default credentials in production!

## Container Names
- Web: `sports_api_web`
- Database: `sports_api_postgres`