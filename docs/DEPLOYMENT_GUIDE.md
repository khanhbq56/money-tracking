# Money Tracking App Deployment Guide

## Table of Contents
1. [Google Cloud Console Setup](#google-cloud-console-setup)
2. [Railway Deployment](#railway-deployment)
3. [Environment Variables](#environment-variables)
4. [Common Issues](#common-issues)

## Google Cloud Console Setup

### 1. Create OAuth 2.0 Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Set **Application type** to **Web application**
6. Add **Authorized redirect URIs**:
   - For production: `https://your-domain.railway.app/auth/oauth/google/callback/`
   - For development: `http://localhost:8000/auth/oauth/google/callback/`
   - For backward compatibility: `https://your-domain.railway.app/auth/google/callback/`

### 2. Enable Required APIs
1. Go to **APIs & Services** → **Library**
2. Enable the following APIs:
   - Google+ API
   - People API
   - Gmail API (if needed)

## Railway Deployment

### 1. Connect Repository
1. Go to [Railway](https://railway.app/)
2. Create new project
3. Connect your GitHub repository
4. Select the main branch

### 2. Configure Build Settings
Railway should auto-detect Django. If not, add these build settings:
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command**: `gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:$PORT`

### 3. Environment Variables
Add these environment variables in Railway dashboard:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=expense_tracker.settings.production
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Google OAuth (Use GOOGLE_OAUTH2_* naming for Railway)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# Optional: Custom redirect URI
GOOGLE_OAUTH_REDIRECT_URI=https://your-domain.railway.app/auth/oauth/google/callback/

# Security
ALLOWED_HOSTS=your-domain.railway.app,healthcheck.railway.app
```

## Environment Variables

### Production (Railway)
```bash
DJANGO_SETTINGS_MODULE=expense_tracker.settings.production
SECRET_KEY=your-django-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@host:port/database
GOOGLE_OAUTH2_CLIENT_ID=your-google-oauth-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-oauth-client-secret
ALLOWED_HOSTS=your-domain.railway.app,healthcheck.railway.app
```

### Development (Local)
Create a `.env` file in your project root:
```bash
DJANGO_SETTINGS_MODULE=expense_tracker.settings.development
SECRET_KEY=your-local-secret-key
DEBUG=True
GOOGLE_OAUTH_CLIENT_ID=your-google-oauth-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-oauth-client-secret
```

## Common Issues

### 1. Google OAuth Redirect Mismatch
**Error**: `redirect_uri_mismatch`
**Solution**: 
- Check that redirect URI in Google Cloud Console matches exactly
- Production: `https://your-domain.railway.app/auth/oauth/google/callback/`
- Development: `http://localhost:8000/auth/oauth/google/callback/`

### 2. HTTPS Required for OAuth
**Error**: `(insecure_transport) OAuth 2 MUST utilize https`
**Solution**: 
- Development settings automatically set `OAUTHLIB_INSECURE_TRANSPORT=1`
- Production uses HTTPS by default

### 3. Invalid HTTP_HOST header
**Error**: `Invalid HTTP_HOST header`
**Solution**: Add domain to `ALLOWED_HOSTS` in environment variables

### 4. Session Issues
**Error**: Users not staying logged in
**Solution**: 
- Check session settings in production.py
- Ensure `SESSION_COOKIE_SECURE=True` in production
- Ensure `SESSION_COOKIE_SECURE=False` in development

### 5. Database Migration Issues
**Error**: Migration failures during deployment
**Solution**:
- Ensure migrations are committed to git
- Check DATABASE_URL format
- Manually run migrations: `python manage.py migrate`

### 6. Static Files Not Loading
**Error**: CSS/JS files not found
**Solution**:
- Run `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings
- Ensure staticfiles app is in INSTALLED_APPS

## Security Checklist

- [ ] DEBUG=False in production
- [ ] SECRET_KEY is unique and secure
- [ ] DATABASE_URL uses SSL
- [ ] SESSION_COOKIE_SECURE=True in production
- [ ] CSRF_COOKIE_SECURE=True in production
- [ ] ALLOWED_HOSTS properly configured
- [ ] Google OAuth credentials are secure

## Performance Tips

1. Use Railway's built-in PostgreSQL for production
2. Enable Redis for session storage (optional)
3. Configure proper logging levels
4. Use CDN for static files (optional)
5. Monitor with Railway's built-in metrics

## Support

For issues:
1. Check Railway deployment logs
2. Check Django debug logs
3. Verify environment variables
4. Test Google OAuth configuration
5. Check database connectivity 