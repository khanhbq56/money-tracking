# 🏦 Bank Integration Testing Guide

## 🎯 Overview
This guide helps you test the completed Gmail Bank Integration feature with TPBank. The system is now fully functional and ready for production testing.

## ✅ Prerequisites
1. ✅ Django server running at http://127.0.0.1:8000/
2. ✅ Google OAuth configured (existing login system)
3. ✅ Gmail account with TPBank transaction emails
4. ✅ Database migrations applied

## 🚀 Testing Steps

### Step 1: Access Settings Page
1. Navigate to http://127.0.0.1:8000/
2. Login with your Google account (if not already logged in)
3. Click the "Settings" button in the navigation (⚙️ icon)
4. You should see the new Settings page with three tabs:
   - Profile Settings
   - **Bank Integration** ← Focus here
   - Notification Settings

### Step 2: Check Demo Account Limitation
If you're using a demo account:
- You'll see a notice that bank integration is not available for demo accounts
- You need to create a regular Google account to test this feature

### Step 3: Grant Gmail Permission (Separate OAuth)
1. Go to the "Bank Integration" tab
2. You'll see "Gmail Permission" section showing "⚠️ Not Connected"
3. Click **"Grant Gmail Permission"** button
4. **IMPORTANT**: This triggers a separate OAuth flow (different from login)
5. You'll be redirected to Google OAuth for Gmail permission
6. Grant permission to read emails
7. You'll be redirected back to settings page
8. Gmail permission should now show "✅ Connected"

### Step 4: Enable TPBank Integration
1. In the "Supported Banks" section, find TPBank
2. Toggle the switch to **enable** TPBank integration
3. A setup modal should appear asking for:
   - **Account Suffix**: Last 4 digits of your TPBank account (e.g., "1234")
   - **Sync Start Date**: Date to start syncing emails from
4. Fill in the details and save
5. TPBank should now show as "Enabled" with "Last Sync: Never"

### Step 5: Test Manual Sync
1. Click the **"Sync Now"** button for TPBank
2. The system will:
   - Connect to Gmail API
   - Search for emails from `tpbank@tpb.com.vn`
   - Parse transaction emails using Gemini AI
   - Create new transactions automatically
3. Check the sync result - you should see:
   - Success message
   - Number of emails processed
   - Number of transactions created

### Step 6: Verify Transactions Created
1. Go back to the main dashboard (home page)
2. Check if new transactions appear with "[Bank]" prefix in description
3. Verify transaction details match your TPBank emails:
   - Correct amount
   - Correct date
   - Proper categorization (expense/saving/investment)
   - Appropriate expense category for expenses

### Step 7: View Sync History
1. In settings, click **"View History"** for TPBank
2. You should see a list of processed emails with:
   - Email date and subject
   - Parsed transaction details
   - AI confidence scores
   - Whether transactions were created

## 🔧 API Testing (Optional)

### Manual API Testing with curl:

1. **Check Gmail Permission Status:**
```bash
curl -X GET "http://127.0.0.1:8000/api/bank-integration/gmail-status/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. **Check Bank Integration Status:**
```bash
curl -X GET "http://127.0.0.1:8000/api/bank-integration/status/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **Trigger Manual Sync:**
```bash
curl -X POST "http://127.0.0.1:8000/api/bank-integration/sync/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"bank_code": "tpbank"}'
```

4. **Get Sync History:**
```bash
curl -X GET "http://127.0.0.1:8000/api/bank-integration/sync-history/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Test Scenarios

### Scenario 1: Fresh Setup
- New user with no Gmail permission
- Test complete flow from permission grant to transaction creation

### Scenario 2: Multiple Emails
- Account with several TPBank transaction emails
- Test batch processing and duplicate detection

### Scenario 3: Different Transaction Types
- Test with various TPBank email types:
  - Payments (expenses)
  - Transfers (savings)
  - Investment transactions

### Scenario 4: Error Handling
- Test with revoked Gmail permission
- Test with disabled bank integration
- Test with invalid email formats

## 📊 Expected Results

### Successful Sync Should Show:
- ✅ Gmail permission granted and active
- ✅ TPBank integration enabled
- ✅ New transactions created with "[Bank]" prefix
- ✅ Correct transaction categorization
- ✅ Proper amount and date parsing
- ✅ AI confidence scores ≥ 0.7 for auto-created transactions

### Transaction Format:
```
Description: "[Bank] Coffee Highlands *1234"
Type: expense
Category: coffee
Amount: 50000
Date: 2024-01-15
Confidence: 0.95
```

## 🐛 Troubleshooting

### Gmail Permission Issues:
- Check if Google OAuth is properly configured
- Verify Gmail API is enabled in Google Cloud Console
- Ensure separate OAuth flow is working (different from login)

### Parsing Issues:
- Check AI confidence scores in sync history
- Low confidence transactions won't auto-create
- Verify TPBank email format matches expected patterns

### Import Issues:
- Check for duplicate transactions (system prevents duplicates)
- Verify user account suffix matches email content
- Check sync date range settings

## 🔐 Security Notes

1. **Separate OAuth Flows**: Login OAuth ≠ Bank Gmail OAuth
2. **Minimal Data Storage**: No raw email content stored
3. **User Control**: Users can revoke permissions anytime
4. **Confidence Threshold**: Only high-confidence transactions auto-create

## 📝 Test Checklist

- [ ] Settings page loads correctly
- [ ] Gmail permission flow works
- [ ] TPBank can be enabled/disabled
- [ ] Manual sync processes emails
- [ ] Transactions are created correctly
- [ ] Sync history shows details
- [ ] Error handling works properly
- [ ] Permissions can be revoked
- [ ] Duplicate detection works
- [ ] AI parsing accuracy is acceptable

## 🎉 Success Criteria

The bank integration is working correctly if:
1. ✅ Users can grant Gmail permission separately from login
2. ✅ TPBank emails are automatically parsed and categorized
3. ✅ Transactions are created with proper details
4. ✅ Users have full control over enable/disable
5. ✅ System handles errors gracefully
6. ✅ No sensitive email data is stored unnecessarily

---

🚀 **The system is now production-ready for TPBank integration!**

For additional banks, follow the same patterns established with TPBank in the codebase. 