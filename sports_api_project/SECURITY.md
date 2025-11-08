# Security Configuration Guide

## Environment Variables (.env file)

This project uses environment variables to store sensitive configuration data. **Never commit the `.env` file to version control**.

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | `your-secret-key-here` |
| `POSTGRES_DB` | Database name | `sports_db` |
| `POSTGRES_USER` | Database username | `sports_user` |
| `POSTGRES_PASSWORD` | Database password | `secure-password-123` |
| `POSTGRES_HOST` | Database host | `db` (for Docker) or `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `DEBUG` | Debug mode (True/False) | `False` (production) |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `yourdomain.com,localhost` |

### Security Settings

| Variable | Description | Production Value |
|----------|-------------|------------------|
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS | `True` |
| `SECURE_HSTS_SECONDS` | HSTS max age | `31536000` (1 year) |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Include subdomains in HSTS | `True` |
| `SECURE_HSTS_PRELOAD` | Enable HSTS preload | `True` |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `True` |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | `True` |
| `ADMIN_URL` | Custom admin URL | `secret-admin/` |

## Setup Instructions

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Generate a new SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

3. **Update database credentials:**
   - Use strong passwords
   - Never use default credentials in production

4. **Configure security settings for production:**
   - Set `DEBUG=False`
   - Enable HTTPS-related settings
   - Update `ALLOWED_HOSTS` with your domain

## File Security

### Files that MUST be in .gitignore:
- `.env` - Contains all secrets
- `*.log` - May contain sensitive information
- `db.sqlite3` - Local database files
- `__pycache__/` - Python cache files
- `media/` - User-uploaded files

### Files that SHOULD be committed:
- `.env.example` - Template for environment variables
- `.gitignore` - Git ignore rules
- `requirements.txt` - Python dependencies
- All source code files

## Production Checklist

- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` generated
- [ ] Strong database passwords
- [ ] `ALLOWED_HOSTS` configured for your domain
- [ ] HTTPS enabled
- [ ] Security headers enabled
- [ ] Custom admin URL set
- [ ] `.env` file never committed to git
- [ ] Regular security updates

## Docker Security

When using Docker:
- Use secrets management for production
- Don't expose database ports unnecessarily
- Use non-root users in containers
- Regularly update base images
- Scan images for vulnerabilities

## Monitoring

Consider adding these to your production setup:
- Log monitoring
- Security scanning
- Database monitoring
- Performance monitoring
- Error tracking (e.g., Sentry)

## Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)