# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-06-14 - Multi-User Release 🎉

### 🚀 Major Features Added
- **Complete Multi-User Support**: Full user isolation with secure authentication
- **Google OAuth Integration**: Secure login with Google accounts
- **Demo Account System**: Temporary accounts for testing with auto-expiration
- **User Data Isolation**: All transactions, chat messages, and data are user-specific

### 🔐 Security Enhancements
- **Authentication Required**: All API endpoints now require user authentication
- **Data Privacy**: Users can only access their own data
- **CSRF Protection**: Enhanced security on all forms and API calls
- **Session Management**: Secure session handling with proper expiration

### 🗄️ Database Changes
- **User Relationships**: Added user foreign keys to Transaction, MonthlyTotal, and ChatMessage models
- **Data Migration**: Automated migration of existing data to multi-user structure
- **Performance Optimization**: Added database indexes for user-filtered queries
- **Connection Pooling**: Enhanced database configuration for multi-user load

### 🌐 API Improvements
- **User-Scoped Endpoints**: All APIs now filter data by current user
- **Enhanced Error Handling**: Better error messages for authentication failures
- **Consistent Response Format**: Standardized API response structure
- **Rate Limiting**: Protection against abuse (future enhancement)

### 🎨 Frontend Updates
- **URL Fixes**: Updated all frontend API calls to use correct endpoints
- **User Context**: Added user-specific UI elements
- **Authentication Flow**: Improved login/logout experience
- **Legal Consent**: Terms of service and privacy policy acceptance

### 🔧 Infrastructure
- **File Organization**: Reorganized project structure with docs/ and scripts/ folders
- **Deployment Scripts**: Enhanced Railway deployment with multi-user support
- **Production Settings**: Optimized settings for multi-user production environment
- **Monitoring**: Enhanced logging for multi-user operations

### 📊 Specific Changes

#### Models Updated
```python
# Added user relationships to:
- Transaction.user (ForeignKey to User)
- MonthlyTotal.user (ForeignKey to User) 
- ChatMessage.user (ForeignKey to User)
```

#### API Endpoints Updated
```python
# All endpoints now include authentication:
- GET /api/transactions/ - User's transactions only
- POST /api/chat/process/ - User's chat messages only
- GET /api/chat/calendar/{year}/{month}/ - User's calendar data only
- GET /api/monthly-totals/ - User's monthly totals only
```

#### Authentication System
```python
# New authentication features:
- Google OAuth with social-auth-app-django
- Demo account creation with auto-expiration
- Legal consent tracking
- Session-based authentication for APIs
```

### 🐛 Bug Fixes
- Fixed calendar API URL routing from `/api/ai_chat/` to `/api/chat/`
- Fixed daily summary API authentication requirements
- Resolved NULL user field issues in existing data
- Fixed FutureProjectionCalculator to work with user context

### 🔄 Migration Guide

#### For Existing Users
1. **Backup your database** before upgrading
2. **Run the deployment script**: `./scripts/deploy_migrations.sh`
3. **Verify data integrity** with the built-in verification tools
4. **Update environment variables** to enable multi-user settings

#### For New Deployments
1. **Set environment variables**:
   ```env
   ENABLE_MULTI_USER=true
   DEFAULT_USER_LIMIT=1000
   ```
2. **Deploy using Railway** with the updated configuration
3. **Access via demo account** or Google OAuth

### 📁 File Structure Changes
```
# New organization:
├── docs/                   # Documentation (moved from root)
│   ├── MULTI_USER_MIGRATION_PLAN.md
│   ├── LOGIN_IMPLEMENTATION_PLAN.md
│   └── GOOGLE_OAUTH_SETUP.md
├── scripts/                # Deployment scripts (moved from root)
│   ├── build.sh
│   ├── start.sh
│   ├── migrate.sh
│   └── deploy_migrations.sh (new)
└── ... (existing structure)
```

### ⚡ Performance Improvements
- Database connection pooling for multi-user load
- Optimized queries with user-specific indexes
- Enhanced caching configuration
- Reduced database calls with select_related/prefetch_related

### 🔮 Future Enhancements
- Rate limiting and API throttling
- Advanced user analytics
- Team/family account sharing
- Export/import functionality
- Mobile app development

---

## [1.0.0] - 2025-06-01 - Initial Release

### 🌟 Initial Features
- Single-user expense tracking
- AI-powered transaction categorization
- Calendar-based interface
- Voice input support
- Future projection simulator
- Multi-language support (Vietnamese/English)

### 🛠️ Technology Stack
- Django 5.x backend
- Google Gemini AI integration
- FullCalendar.js frontend
- Tailwind CSS styling
- Railway deployment

### 📊 Core Functionality
- Transaction management (Expense/Saving/Investment)
- Monthly totals calculation
- AI chat interface
- Calendar visualization
- Basic reporting and analytics

---

## Development Notes

### Version Numbering
- **Major version**: Breaking changes, major feature additions
- **Minor version**: New features, backwards compatible
- **Patch version**: Bug fixes, small improvements

### Release Process
1. Development and testing
2. Documentation updates
3. Migration scripts preparation
4. Deployment to staging
5. Production release
6. Post-release monitoring

### Support Policy
- **Current version (2.x)**: Full support and active development
- **Previous version (1.x)**: Security fixes only for 6 months
- **Migration assistance**: Available for major version upgrades 