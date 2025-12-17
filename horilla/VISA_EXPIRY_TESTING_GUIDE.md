# Visa Expiry Notification Testing Guide

## Overview
The visa expiry notification system automatically sends emails to HR admins (superusers) and the employee when a new employee is added with a visa expiry date within the next 31 days.

## Email Templates Created
1. **Admin Notification**: `templates/emails/visa_expiry_admin_notification.html`
2. **Employee Notification**: `templates/emails/visa_expiry_notification.html`

## Prerequisites
✅ Email configuration is already set up in your `.env` file:
- EMAIL_HOST_USER: sarwarbmthr@gmail.com
- Email is configured and ready to use

## How It Works
The signal `employee_post_save` in `employee/signals.py` triggers when:
1. A **new** employee is created (not on updates)
2. The employee has a `visa_expire_date` field set
3. The visa expires within **0 to 30 days** from today

## Testing Steps

### Step 1: Verify Email Configuration
1. Make sure your Django development server is running
2. Email settings are already configured in `.env`

### Step 2: Check Superusers (HR Admins)
The system sends emails to all superusers. To check superusers:
```python
# Open Django shell
python manage.py shell

# Check superusers
from django.contrib.auth.models import User
superusers = User.objects.filter(is_superuser=True)
for user in superusers:
    print(f"Username: {user.username}, Email: {user.email}")
```

### Step 3: Add Test Employee with Visa Expiry Date

**Option A: Through Django Admin/Web Interface**
1. Go to your HRM application
2. Navigate to Employee → Add Employee
3. Fill in the required fields:
   - **First Name**: Test Employee
   - **Email**: test.employee@example.com (use a valid email you can check)
   - **Phone**: +1234567890
   - **Visa Expiry Date**: Set a date within 31 days (e.g., 15 days from today)
4. Save the employee

**Option B: Through Django Shell**
```python
python manage.py shell

from datetime import date, timedelta
from employee.models import Employee

# Create test employee with visa expiring in 15 days
visa_date = date.today() + timedelta(days=15)

employee = Employee.objects.create(
    employee_first_name="John",
    employee_last_name="Doe",
    email="john.doe@example.com",  # Use your test email
    phone="+1234567890",
    visa_expire_date=visa_date,
    is_active=True
)

print(f"Employee created: {employee.get_full_name()}")
print(f"Visa expiry date: {employee.visa_expire_date}")
print(f"Days until expiry: {(visa_date - date.today()).days}")
```

### Step 4: Check Email Delivery

**Check these locations for emails:**
1. **Console output**: If using console backend, emails will appear in terminal
2. **Email inbox**: Check the superuser's email inbox
3. **Employee email**: Check the test employee's email inbox
4. **Django admin Email Log**: Check `base/EmailLog` model if logging is enabled

### Step 5: Verify Email Content

**Admin Email Should Contain:**
- Subject: "Employee visa expiring: [Employee Name]"
- Employee details (name, ID, email, phone, department)
- Visa expiry date
- Number of days until expiry
- Action items for HR

**Employee Email Should Contain:**
- Subject: "Your visa will expire soon"
- Employee name
- Visa expiry date
- Number of days until expiry
- Action required steps
- Contact HR information

### Step 6: Test Different Scenarios

**Test Case 1: Visa expiring today**
```python
visa_date = date.today()
```

**Test Case 2: Visa expiring in 30 days (boundary)**
```python
visa_date = date.today() + timedelta(days=30)
```

**Test Case 3: Visa expiring in 31 days (should NOT send email)**
```python
visa_date = date.today() + timedelta(days=31)
```

**Test Case 4: Visa already expired (should NOT send email)**
```python
visa_date = date.today() - timedelta(days=1)
```

**Test Case 5: No visa expiry date (should NOT send email)**
```python
employee = Employee.objects.create(
    employee_first_name="Jane",
    employee_last_name="Smith",
    email="jane.smith@example.com",
    phone="+1234567891",
    # visa_expire_date=None  # Not set
)
```

## Troubleshooting

### If emails are not being sent:

1. **Check Django logs/console** for any errors
2. **Verify email configuration** in `.env`
3. **Test email backend** manually:
```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email.',
    'sarwarbmthr@gmail.com',
    ['your-test-email@example.com'],
    fail_silently=False,
)
```

4. **Check signal is connected**:
```python
from django.db.models.signals import post_save
from employee.models import Employee

# List all receivers
for receiver in post_save._live_receivers(Employee):
    print(receiver)
```

5. **Verify superuser emails are set**:
```python
from django.contrib.auth.models import User
superusers = User.objects.filter(is_superuser=True, email__isnull=False)
print([u.email for u in superusers])
```

## Expected Behavior

✅ **Should send email when:**
- New employee is created (not updated)
- Visa expiry date is set
- Visa expires within 0-30 days from today
- Superuser emails exist

❌ **Should NOT send email when:**
- Employee is being updated (only on creation)
- Visa expiry date is > 30 days away
- Visa expiry date is in the past (< 0 days)
- No visa expiry date is set
- No superusers with emails exist

## Quick Test Command

Run this in Django shell for quick testing:
```python
from datetime import date, timedelta
from employee.models import Employee

# Clean up any previous test employees
Employee.objects.filter(email__startswith='test.visa').delete()

# Create test employee
visa_date = date.today() + timedelta(days=10)
emp = Employee.objects.create(
    employee_first_name="Visa",
    employee_last_name="Test",
    email="test.visa.employee@example.com",
    phone="+9876543210",
    visa_expire_date=visa_date,
    is_active=True
)

print(f"✅ Test employee created!")
print(f"   Name: {emp.get_full_name()}")
print(f"   Email: {emp.email}")
print(f"   Visa expires: {emp.visa_expire_date}")
print(f"   Days until expiry: {(visa_date - date.today()).days}")
print(f"\nCheck emails sent to:")
from django.contrib.auth.models import User
for admin in User.objects.filter(is_superuser=True):
    print(f"   - Admin: {admin.email}")
print(f"   - Employee: {emp.email}")
```

## Dashboard Viewing

After creating employees with upcoming visa expiries:
1. Go to **Employee Dashboard**
2. You should see **Visa Expiry** widget showing employees
3. Click **"View all"** to see the full visa expiry list at `/visa-expiry-list`

## Notes
- The system uses `fail_silently=True`, so email errors won't crash the application
- Fallback plain text emails are sent if HTML templates fail
- Both admin and employee receive notifications simultaneously
- The signal only triggers on employee creation, not updates
