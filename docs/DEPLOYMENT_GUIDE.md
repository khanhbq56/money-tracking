# Deployment Guide

## Railway Deployment

### Environment Variables

Set these environment variables in your Railway deployment:

```bash
# Django Settings
DJANGO_SECRET_KEY="your-secret-key-here"
DEBUG="False"
DJANGO_SETTINGS_MODULE="expense_tracker.settings.production"

# Localization
LANGUAGE_CODE="vi"
TIME_ZONE="Asia/Ho_Chi_Minh"

# Allowed hosts (comma-separated)
ALLOWED_HOSTS="localhost,127.0.0.1,healthcheck.railway.app,your-app-name.up.railway.app"

# Database (Railway automatically provides this)
DATABASE_URL="${{Postgres.DATABASE_URL}}"

# Google OAuth Settings (IMPORTANT: Use correct naming)
GOOGLE_OAUTH_CLIENT_ID="your-google-oauth-client-id"
GOOGLE_OAUTH_CLIENT_SECRET="your-google-oauth-client-secret"  
GOOGLE_OAUTH_REDIRECT_URI="https://your-app-name.up.railway.app/auth/oauth/google/callback/"

# AI Settings
GEMINI_API_KEY="your-gemini-api-key"
```

### Fix for Current Deployment

Your current `.env` has these issues:

1. **Incorrect OAuth variable names**: Change from `GOOGLE_OAUTH2_*` to `GOOGLE_OAUTH_*`
2. **Wrong redirect URI**: Should be `/auth/oauth/google/callback/` not `/auth/google/callback/`

#### Updated .env for your deployment:

```bash
DJANGO_SECRET_KEY="pqbw(ro1t97wbfb&rj+q5s%0d(%(&lc1h7-+a9x3d7lbjj%7e_"
GEMINI_API_KEY="AIzaSyDXRY0ECgjUeBwdgSaw6UGJr3eqh85rEgk"
DEBUG="False"
DJANGO_SETTINGS_MODULE="expense_tracker.settings.production"
LANGUAGE_CODE="vi"
TIME_ZONE="Asia/Ho_Chi_Minh"
ALLOWED_HOSTS="localhost,127.0.0.1,healthcheck.railway.app,money-tracking-production.up.railway.app"
DATABASE_URL="${{Postgres.DATABASE_URL}}"

# Fixed OAuth variables (changed from GOOGLE_OAUTH2_* to GOOGLE_OAUTH_*)
GOOGLE_OAUTH_CLIENT_ID="515963526992-q8ga8lhcd59a0s6v2i6voerf0tng5lcd.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET="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"
GOOGLE_OAUTH_REDIRECT_URI="https://money-tracking-production.up.railway.app/auth/oauth/google/callback/"
```

### Google OAuth Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to APIs & Services > Credentials
4. Edit your OAuth 2.0 Client ID
5. Update Authorized redirect URIs to:
   ```
   https://money-tracking-production.up.railway.app/auth/oauth/google/callback/
   ```

### Deployment Steps

1. Update environment variables in Railway dashboard
2. Update Google OAuth redirect URI in Google Cloud Console
3. Redeploy the application
4. Test OAuth login functionality

### Verification

After deployment, verify:
- ✅ App loads without ALLOWED_HOSTS error
- ✅ Google OAuth login works
- ✅ Demo account creation works
- ✅ Session management works properly 