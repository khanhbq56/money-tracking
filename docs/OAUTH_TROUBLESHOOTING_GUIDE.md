# 🔧 OAuth Troubleshooting Guide

This guide helps resolve common OAuth authentication issues in Money Tracker.

## 🎯 **Quick Diagnosis**

Run the OAuth debug script to check your configuration:
```bash
python debug_oauth.py
```

Or visit the debug page (development only):
```
http://localhost:8000/auth/debug/
```

---

## 🚨 **Common OAuth Errors**

### **1. Scope Mismatch Error**
**Error:** `Scope has changed from "openid email profile" to "openid email gmail.readonly profile"`

**Cause:** Google automatically includes previously granted scopes (like Gmail permissions) when user logs in.

**Solution:** 
- ✅ **Already Fixed:** Code now handles scope mismatches gracefully
- The error is harmless and login should proceed successfully
- If it persists, revoke app permissions in Google Account and try again

**Prevention:** Use `include_granted_scopes='false'` in OAuth flow

---

### **2. Redirect URI Mismatch**
**Error:** `redirect_uri_mismatch`

**Cause:** Google Console not configured with correct redirect URI.

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services → Credentials**
3. Edit OAuth Client ID: `515963526992-q8ga8lhcd59a0s6v2i6voerf0tng5lcd`
4. Add these **Authorized redirect URIs**:
   ```
   http://localhost:8000/auth/oauth/google/callback/
   http://127.0.0.1:8000/auth/oauth/google/callback/
   https://money-tracking-production.up.railway.app/auth/oauth/google/callback/
   ```
5. Save and wait 5-10 minutes for changes to propagate

---

### **3. OAuth State Mismatch**
**Error:** `OAuth state mismatch - potential CSRF attack`

**Cause:** 
- Session expired during OAuth flow
- Multiple browser tabs/windows
- CSRF protection triggered

**Solution:**
- Clear browser session and try again
- Use only one browser tab
- Check if cookies are enabled

---

### **4. OAuth Client Error**
**Error:** `invalid_client` or `unauthorized_client`

**Cause:**
- Wrong Client ID/Secret
- OAuth consent screen not published
- APIs not enabled

**Solution:**
1. Verify Client ID and Secret in environment variables
2. Publish OAuth consent screen in Google Console
3. Enable required APIs:
   - Google+ API (legacy) or People API
   - Gmail API (for bank integration)

---

### **5. Access Denied**
**Error:** `access_denied`

**Cause:**
- User cancelled OAuth flow
- App not verified by Google
- Admin restrictions

**Solution:**
- User should complete OAuth flow
- For production: Verify app with Google
- Check Google Workspace admin restrictions

---

## 🛠 **Configuration Checklist**

### **Environment Variables**
```bash
✅ GOOGLE_OAUTH2_CLIENT_ID=your-client-id.googleusercontent.com
✅ GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
✅ GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/auth/oauth/google/callback/
✅ SITE_URL=http://localhost:8000
```

### **Google Console Setup**
```
✅ OAuth 2.0 Client ID created
✅ Authorized redirect URIs added
✅ OAuth consent screen configured
✅ Required APIs enabled
✅ Test users added (for development)
```

### **Django Settings**
```python
✅ GOOGLE_OAUTH2_SCOPES defined correctly
✅ Middleware order correct
✅ URL patterns properly configured
✅ Session configuration valid
```

---

## 🔍 **Advanced Debugging**

### **Check OAuth Flow Step by Step**

1. **Initiation Check:**
   ```bash
   curl -v http://localhost:8000/auth/oauth/google/
   ```

2. **Token Exchange Check:**
   - Look for scope mismatch in Django logs
   - Check state parameter validation
   - Verify redirect URI matches exactly

3. **User Info Check:**
   - Verify ID token validation
   - Check user creation/update logic
   - Monitor session establishment

### **Log Analysis**

Enable detailed logging in `settings/development.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

Common log patterns:
- ✅ `OAuth URL generated successfully`
- ❌ `OAuth state mismatch`
- ❌ `Scope has changed from X to Y`
- ✅ `User {email} logged in successfully`

---

## 🚀 **Production Deployment**

### **Environment Differences**

| Setting | Development | Production |
|---------|-------------|------------|
| Redirect URI | `http://localhost:8000/auth/oauth/google/callback/` | `https://your-domain.com/auth/oauth/google/callback/` |
| SESSION_COOKIE_SECURE | `False` | `True` |
| OAUTHLIB_INSECURE_TRANSPORT | `'1'` | Not set |

### **Railway Deployment**

Update environment variables in Railway:
```bash
GOOGLE_OAUTH2_REDIRECT_URI=https://money-tracking-production.up.railway.app/auth/oauth/google/callback/
SESSION_COOKIE_SECURE=True
DEBUG=False
```

---

## 🔒 **Security Best Practices**

1. **Minimal Scopes:** Only request necessary permissions
2. **State Validation:** Always validate state parameter
3. **HTTPS Only:** Use HTTPS in production
4. **Scope Separation:** Separate login OAuth from feature OAuth
5. **Token Management:** Properly handle token refresh and expiry

---

## 📞 **Getting Help**

If OAuth issues persist:

1. **Run debug script:** `python debug_oauth.py`
2. **Check logs:** Look for specific error patterns
3. **Test with debug page:** Visit `/auth/debug/` in development
4. **Verify Google Console:** Double-check all settings
5. **Clear cache:** Clear browser data and try again

Remember: OAuth errors are often configuration issues, not code bugs. The fixes in this guide should resolve 95% of authentication problems. 