# 🔐 Google OAuth 2.0 Setup Guide

This guide will help you set up Google OAuth authentication for Money Tracker.

## 📋 **Prerequisites**

- Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- Money Tracker project running locally or deployed

---

## 🚀 **Step 1: Create Google Cloud Project**

1. **Go to Google Cloud Console**
   - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create New Project**
   - Click "Select a project" dropdown
   - Click "New Project"
   - Enter project name: `money-tracker-oauth`
   - Click "Create"

3. **Select Your Project**
   - Make sure your new project is selected in the project dropdown

---

## 🔧 **Step 2: Enable Google+ API**

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" > "Library"

2. **Enable Required APIs**
   - Search for "Google+ API" and enable it
   - Search for "People API" and enable it (recommended)

---

## 🔑 **Step 3: Create OAuth 2.0 Credentials**

1. **Go to Credentials Page**
   - In the left sidebar, click "APIs & Services" > "Credentials"

2. **Create OAuth Consent Screen**
   - Click "OAuth consent screen" tab
   - Choose "External" user type
   - Click "Create"

3. **Configure OAuth Consent Screen**
   ```
   App name: Money Tracker
   User support email: your-email@gmail.com
   App logo: (optional - upload your app logo)
   App domain: your-domain.com (if deployed)
   Developer contact email: your-email@gmail.com
   ```

4. **Add Scopes (Step 2)**
   - Click "Add or Remove Scopes"
   - Add these scopes:
     - `../auth/userinfo.email`
     - `../auth/userinfo.profile`
     - `openid`
   - Click "Update"

5. **Add Test Users (Step 3)**
   - Add your email and any test user emails
   - Click "Save and Continue"

6. **Create Credentials**
   - Go back to "Credentials" tab
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Name: "Money Tracker Web Client"

7. **Configure Authorized URIs**
   
   **For Local Development:**
   ```
   Authorized JavaScript origins:
   - http://localhost:8000
   - http://127.0.0.1:8000
   
   Authorized redirect URIs:
   - http://localhost:8000/auth/google/callback/
   - http://127.0.0.1:8000/auth/google/callback/
   ```
   
   **For Production:**
   ```
   Authorized JavaScript origins:
   - https://yourdomain.com
   
   Authorized redirect URIs:
   - https://yourdomain.com/auth/google/callback/
   ```

8. **Get Credentials**
   - Click "Create"
   - Copy the Client ID and Client Secret
   - Download the JSON file (optional, for backup)

---

## ⚙️ **Step 4: Configure Environment Variables**

1. **Update your `.env` file:**
   ```bash
   # Google OAuth 2.0 Configuration
   GOOGLE_OAUTH2_CLIENT_ID=your-client-id.googleusercontent.com
   GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
   GOOGLE_OAUTH2_PROJECT_ID=money-tracker-oauth
   
   # OAuth redirect URI (update for production)
   GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/auth/google/callback/
   ```

2. **For Production Deployment:**
   ```bash
   # Update redirect URI for your domain
   GOOGLE_OAUTH2_REDIRECT_URI=https://yourdomain.com/auth/google/callback/
   ```

---

## 🧪 **Step 5: Test OAuth Integration**

1. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

2. **Test Login Flow**
   - Go to `http://localhost:8000`
   - Login modal should appear
   - Click "Sign in with Google"
   - Complete OAuth flow
   - Verify successful login

3. **Test Demo Account**
   - Click "Try with Demo Account"
   - Accept terms and privacy policy
   - Verify demo account creation

---

## 🔒 **Security Best Practices**

### **Minimal Permissions**
- Only request necessary scopes: `openid`, `email`, `profile`
- Never request access to Google Drive, Calendar, or other services

### **HTTPS in Production**
- Always use HTTPS for production OAuth
- Update redirect URIs to use `https://`

### **Environment Security**
- Keep client secret secure and never commit to version control
- Use environment variables or secure secret management
- Rotate credentials if compromised

### **CSRF Protection**
- OAuth state parameter prevents CSRF attacks
- Session-based state validation implemented

---

## 🚨 **Troubleshooting**

### **Common Errors**

1. **"Error 400: redirect_uri_mismatch"**
   - Verify redirect URI matches exactly in Google Console
   - Check for trailing slashes
   - Ensure HTTP vs HTTPS matches

2. **"Error 403: access_denied"**
   - User cancelled OAuth flow
   - Check OAuth consent screen configuration
   - Verify app is not restricted

3. **"Error 401: invalid_client"**
   - Check client ID and secret are correct
   - Verify environment variables are loaded
   - Check for typos in configuration

4. **"Error: OAuth2 flow failed"**
   - Check network connectivity
   - Verify APIs are enabled in Google Console
   - Check server logs for detailed error

### **Debug Steps**

1. **Check Django Logs**
   ```bash
   # In development
   python manage.py runserver --verbosity=2
   
   # Check logs for OAuth errors
   tail -f /var/log/django/oauth.log
   ```

2. **Verify Environment Variables**
   ```python
   # In Django shell
   from django.conf import settings
   print(settings.GOOGLE_OAUTH2_CLIENT_ID)
   print(settings.GOOGLE_OAUTH2_CLIENT_SECRET)
   ```

3. **Test API Access**
   ```bash
   # Test if APIs are accessible
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        https://www.googleapis.com/oauth2/v2/userinfo
   ```

---

## 📊 **Production Deployment**

### **Domain Configuration**
1. Update Google Console with production domain
2. Add production redirect URIs
3. Update environment variables
4. Test OAuth flow on production

### **SSL Certificate**
1. Ensure valid SSL certificate
2. Test HTTPS redirect URIs
3. Verify certificate chain

### **Monitoring**
1. Set up OAuth success/failure logging
2. Monitor authentication errors
3. Track user registration metrics

---

## 📝 **Additional Resources**

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google API Console](https://console.developers.google.com/)
- [OAuth 2.0 Scopes](https://developers.google.com/identity/protocols/oauth2/scopes)

---

## 🆘 **Need Help?**

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all URLs and credentials are correct
3. Test with a fresh browser session
4. Contact support: support@moneytracker.app

---

**✅ Setup Complete!** Your Money Tracker application now supports secure Google OAuth authentication with minimal permissions and maximum privacy protection.