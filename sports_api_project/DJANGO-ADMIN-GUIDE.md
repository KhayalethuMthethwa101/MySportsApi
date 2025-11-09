# Django Admin User Management Guide

## Understanding Different Passwords

### 1. PostgreSQL Database Password
- **Location**: `.env` file → `POSTGRES_PASSWORD=your_db_password_here`
- **Purpose**: Connects Django to PostgreSQL database
- **Used by**: Django application to access database
- **Not for**: Django admin login

### 2. Django Admin Password
- **Purpose**: Login to Django admin interface at `/admin/`
- **Created by**: Running `createsuperuser` command
- **Stored**: In Django's `auth_user` table (hashed)

## Creating Django Admin User

### Method 1: Interactive Creation (Recommended)
```bash
# Run this in your project directory
docker-compose exec web python manage.py createsuperuser
```

You'll be prompted for:
- **Username**: Choose an admin username (e.g., `admin`, `khaya`)
- **Email**: Your email address
- **Password**: Choose a secure password for Django admin

### Method 2: Check if Admin User Already Exists
```bash
# Connect to database and check for users
docker-compose exec db psql -U sports_user -d sports_db -c "SELECT id, username, email, is_superuser, is_staff FROM auth_user;"
```

### Method 3: Create Admin User via SQL (if needed)
```bash
# If you need to create a user manually
docker-compose exec web python manage.py shell
```

Then in Python shell:
```python
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'your_chosen_password')
exit()
```

## Accessing Django Admin

1. **Start your containers**:
   ```bash
   docker-compose up -d
   ```

2. **Open browser and go to**:
   ```
   http://localhost:8000/admin/
   ```

3. **Login with**:
   - Username: (the one you created)
   - Password: (the one you chose during superuser creation)

## Managing Django Users

### Reset Password for Existing User
```bash
docker-compose exec web python manage.py changepassword username
```

### List All Django Users
```bash
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
for user in User.objects.all():
    print(f'User: {user.username}, Email: {user.email}, Superuser: {user.is_superuser}, Staff: {user.is_staff}')
"
```

### Delete a User
```bash
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.get(username='username_to_delete').delete()
"
```

## Password Summary

| Password Type | Location | Purpose | How to Set |
|---------------|----------|---------|------------|
| **Database Password** | `.env` file | Django ↔ PostgreSQL connection | Edit `.env` file |
| **Django Admin Password** | Database (hashed) | Login to `/admin/` | `createsuperuser` command |

## Quick Commands Cheat Sheet

```bash
# Create new admin user
docker-compose exec web python manage.py createsuperuser

# Change existing user password
docker-compose exec web python manage.py changepassword admin

# Access database directly
docker-compose exec db psql -U sports_user -d sports_db

# Check Django users in database
docker-compose exec db psql -U sports_user -d sports_db -c "SELECT username, email, is_superuser FROM auth_user;"

# Django shell for advanced operations
docker-compose exec web python manage.py shell
```

## Troubleshooting

### Can't Access Admin Panel?
1. Make sure containers are running: `docker-compose ps`
2. Check if superuser exists: Run user list command above
3. Verify Django is accessible: `curl http://localhost:8000/`

### Forgot Admin Password?
```bash
docker-compose exec web python manage.py changepassword your_username
```

### Need to Create First Admin User?
```bash
docker-compose exec web python manage.py createsuperuser
```

## Security Notes

- Never commit Django admin passwords to git
- Use strong passwords for admin accounts
- Regularly update admin passwords
- Consider using environment variables for initial admin setup in production