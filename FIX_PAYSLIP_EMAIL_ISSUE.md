# Fix Payslip Email Issue - Troubleshooting Guide

## Problem
You click "Send via mail" → See "Mail processing" message → But emails are NOT being sent to employees

---

## Root Causes & Solutions

### **Issue 1: Gmail App Password Required** ⭐ MOST COMMON

**Problem:** Gmail blocks login from "less secure apps" by default

**Solution:**

#### Option A: Use Gmail App Password (Recommended)

1. **Go to Google Account Settings:**
   - Visit: https://myaccount.google.com/
   - Login with: sarwarbmthr@gmail.com

2. **Enable 2-Step Verification:**
   - Go to Security → 2-Step Verification
   - Enable it if not already enabled

3. **Generate App Password:**
   - Go to Security → App passwords
   - Select app: "Mail"
   - Select device: "Other (Custom name)"
   - Enter: "Horilla HRMS"
   - Click "Generate"
   - **Copy the 16-character password** (e.g., "abcd efgh ijkl mnop")

4. **Update .env file:**
   ```properties
   EMAIL_HOST_PASSWORD="abcdefghijklmnop"  # Remove spaces, use the app password
   ```

5. **Restart Django server**

#### Option B: Enable Less Secure Apps (Not Recommended)

1. Visit: https://myaccount.google.com/lesssecureapps
2. Turn ON "Allow less secure apps"
3. Restart Django server

---

### **Issue 2: EMAIL_USE_TLS Setting**

**Problem:** `.env` file has `EMAIL_USE_SSL="False"` but should use TLS for Gmail

**Current .env:**
```properties
EMAIL_USE_SSL="False"
EMAIL_TIMEOUT="10"
```

**Fix - Add this line:**
```properties
EMAIL_USE_TLS="True"  # Add this line
EMAIL_USE_SSL="False"
EMAIL_TIMEOUT="10"
```

**Complete correct configuration:**
```properties
EMAIL_BACKEND="base.backends.ConfiguredEmailBackend"
DEFAULT_FROM_EMAIL="sarwarbmthr@gmail.com"
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_HOST_USER="sarwarbmthr@gmail.com"
EMAIL_HOST_PASSWORD="your-app-password-here"  # Use App Password
EMAIL_USE_TLS="True"  # IMPORTANT: Add this
EMAIL_USE_SSL="False"
EMAIL_TIMEOUT="10"
```

---

### **Issue 3: Employee Email Addresses Missing**

**Problem:** Employees don't have email addresses in the system

**Check:**
```python
# Run in Django shell
from employee.models import Employee

# Check employees without email
for emp in Employee.objects.filter(is_active=True):
    email = emp.get_mail()
    if not email:
        print(f"❌ {emp.get_full_name()} has NO email")
```

**Solution:**
1. Go to Employee → Employee List
2. Edit each employee
3. Add email address in:
   - **Work Email** (preferred) OR
   - **Personal Email** field

**Note:** `get_mail()` method returns work_email first, then falls back to personal email

---

### **Issue 4: Thread Exception Being Silently Caught**

**Problem:** The `MailSendThread` catches exceptions but only logs them

**Code in `horilla/payroll/threadings/mail.py` (Line 76-80):**
```python
try:
    email.send()
    Payslip.objects.filter(id__in=self.ids).update(sent_to_employee=True)
except Exception as e:
    logger.exception(e)  # Only logs, doesn't show to user
```

**Solution:** Check Django console/logs for exceptions

**Enable detailed logging:**

Add to `horilla/settings.py`:
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
        'payroll': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

### **Issue 5: Dynamic Email Configuration Not Set**

**Problem:** `dynamic_from_email_with_display_name` is None

**Check in `send_slip()` function:**
```python
if not getattr(email_backend, "dynamic_from_email_with_display_name", None):
    messages.error(request, "Email server is not configured")
    return redirect(filter_payslip)
```

**Solution:**

**Option A: Set in Database**
1. Go to Django Admin
2. Navigate to Base → Dynamic Email Configuration
3. Create/Edit configuration:
   - Host: smtp.gmail.com
   - Port: 587
   - Username: sarwarbmthr@gmail.com
   - Password: [App Password]
   - Use TLS: ✓ Yes
   - From Email: sarwarbmthr@gmail.com
   - Display Name: Horilla HRMS

**Option B: Ensure .env is loaded**
- Restart Django server after changing .env
- Check settings are loaded: `python manage.py shell`
  ```python
  from django.conf import settings
  print(settings.EMAIL_HOST)
  print(settings.EMAIL_HOST_USER)
  ```

---

## Step-by-Step Diagnostic Process

### Step 1: Run Diagnostic Script

```bash
cd horilla
python manage.py shell < DIAGNOSE_PAYSLIP_EMAIL_ISSUE.py
```

This will check:
- ✅ Email configuration
- ✅ Employee email addresses
- ✅ Recent payslips
- ✅ Test email sending
- ✅ Email logs

### Step 2: Test Email Manually

```python
# Run in Django shell
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com'],  # Your email
    fail_silently=False,
)
```

**If this works:** Email config is correct, issue is elsewhere
**If this fails:** Fix email configuration first

### Step 3: Check Django Console

When you click "Send via mail", watch the Django console for errors:

```bash
# Run Django with console output
python manage.py runserver

# Watch for errors like:
# SMTPAuthenticationError
# ConnectionRefusedError
# TimeoutError
```

### Step 4: Check Employee Emails

```python
# Django shell
from payroll.models.models import Payslip

# Get a payslip
payslip = Payslip.objects.first()

# Check employee email
print(payslip.employee_id.get_mail())  # Should print email address
```

### Step 5: Check Email Logs

```python
# Django shell
from base.models import EmailLog

# Check recent logs
for log in EmailLog.objects.all().order_by('-id')[:5]:
    print(f"Status: {log.status}")
    print(f"To: {log.to}")
    print(f"Error: {log.error_message}")
    print("-" * 50)
```

---

## Quick Fix Checklist

### ✅ **Immediate Actions:**

1. **Update .env file:**
   ```properties
   EMAIL_USE_TLS="True"  # Add this line
   EMAIL_HOST_PASSWORD="your-gmail-app-password"  # Use App Password
   ```

2. **Restart Django:**
   ```bash
   # Stop server (Ctrl+C)
   python manage.py runserver
   ```

3. **Test email:**
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test', 'sarwarbmthr@gmail.com', ['your-email@example.com'])
   ```

4. **Check employee emails:**
   - Go to Employee → Employee List
   - Verify each employee has email address

5. **Try sending payslip again:**
   - Payroll → Payslip
   - Select payslip
   - Actions → Send via mail

---

## Common Error Messages & Solutions

### Error: "Email server is not configured"

**Cause:** `dynamic_from_email_with_display_name` is None

**Solution:**
1. Check .env file has all email settings
2. Restart Django server
3. Create DynamicEmailConfiguration in database

### Error: "SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')"

**Cause:** Gmail rejecting login

**Solution:**
1. Use App Password instead of regular password
2. Enable 2-Step Verification
3. Generate App Password from Google Account

### Error: "ConnectionRefusedError: [Errno 111] Connection refused"

**Cause:** Cannot connect to SMTP server

**Solution:**
1. Check EMAIL_HOST is correct: smtp.gmail.com
2. Check EMAIL_PORT is correct: 587
3. Check firewall not blocking port 587
4. Check internet connection

### Error: "SMTPServerDisconnected: Connection unexpectedly closed"

**Cause:** TLS/SSL configuration issue

**Solution:**
1. Set EMAIL_USE_TLS="True"
2. Set EMAIL_USE_SSL="False"
3. Restart Django server

### No Error, But Email Not Received

**Possible Causes:**
1. Email in spam folder
2. Employee email address is wrong
3. Thread exception being caught silently

**Solution:**
1. Check spam/junk folder
2. Verify employee email: `employee.get_mail()`
3. Check Django console for exceptions
4. Check EmailLog for errors

---

## Testing After Fix

### Test 1: Manual Email Test
```python
python manage.py shell

from django.core.mail import send_mail
send_mail('Test', 'Test message', 'sarwarbmthr@gmail.com', ['test@example.com'])
# Should print: 1 (success)
```

### Test 2: Send Single Payslip
1. Go to Payroll → Payslip
2. Click mail icon (📧) on one payslip
3. Confirm
4. Check employee email inbox

### Test 3: Bulk Send
1. Go to Payroll → Payslip
2. Select multiple payslips
3. Actions → Send via mail
4. Confirm
5. Check all employee email inboxes

### Test 4: Verify Sent Status
1. After sending, mail icon should turn GREEN
2. Database: `sent_to_employee` should be True
3. EmailLog should have entries

---

## Prevention

### Best Practices:

1. **Always use App Passwords for Gmail**
   - More secure
   - Doesn't require "less secure apps"
   - Can be revoked independently

2. **Validate employee emails**
   - Add validation in employee form
   - Require email field
   - Check email format

3. **Monitor email logs**
   - Regularly check EmailLog model
   - Set up alerts for failed emails
   - Monitor Django console

4. **Test email configuration**
   - Test after any configuration change
   - Test with different email providers
   - Keep backup SMTP credentials

---

## Code Changes (Optional - For Better Error Handling)

### Improve Error Visibility

**File:** `horilla/payroll/threadings/mail.py`

**Change Line 76-80 from:**
```python
try:
    email.send()
    Payslip.objects.filter(id__in=self.ids).update(sent_to_employee=True)
except Exception as e:
    logger.exception(e)
```

**To:**
```python
try:
    email.send()
    Payslip.objects.filter(id__in=self.ids).update(sent_to_employee=True)
    logger.info(f"✅ Email sent successfully to {employee.get_mail()}")
except Exception as e:
    logger.exception(f"❌ Failed to send email to {employee.get_mail()}: {e}")
    # Optionally: Store error in database for user visibility
```

---

## Summary

### Most Likely Issue: Gmail App Password

**Quick Fix:**
1. Generate Gmail App Password
2. Update EMAIL_HOST_PASSWORD in .env
3. Add EMAIL_USE_TLS="True" to .env
4. Restart Django
5. Test again

### If Still Not Working:

1. Run diagnostic script
2. Check Django console for errors
3. Verify employee email addresses
4. Check EmailLog for error messages
5. Test manual email sending

---

**Document Created:** February 9, 2026  
**Issue:** Payslip emails not sending  
**Status:** Diagnostic and fix guide provided
