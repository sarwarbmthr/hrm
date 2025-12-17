"""
Test script for visa expiry notification system
Run this from Django shell: python manage.py shell < test_visa_notification.py
"""

from datetime import date, timedelta
from django.contrib.auth.models import User
from employee.models import Employee

print("=" * 70)
print("VISA EXPIRY NOTIFICATION TEST SCRIPT")
print("=" * 70)

# Step 1: Check for superusers
print("\n[Step 1] Checking for superusers (HR Admins)...")
superusers = User.objects.filter(is_superuser=True)
if not superusers.exists():
    print("❌ No superusers found! Create a superuser first:")
    print("   python manage.py createsuperuser")
    exit(1)

print(f"✅ Found {superusers.count()} superuser(s):")
for user in superusers:
    email_status = f"✅ {user.email}" if user.email else "❌ No email set!"
    print(f"   - {user.username}: {email_status}")

# Check if all superusers have email addresses
superusers_with_email = [u for u in superusers if u.email]
if not superusers_with_email:
    print("\n⚠️  WARNING: No superusers have email addresses set!")
    print("   Emails will not be sent to admins.")
else:
    print(f"\n✅ {len(superusers_with_email)} admin(s) will receive notifications")

# Step 2: Clean up previous test data
print("\n[Step 2] Cleaning up previous test data...")
deleted_count = Employee.objects.filter(email__startswith='test.visa.').delete()[0]
if deleted_count > 0:
    print(f"✅ Deleted {deleted_count} old test employee(s)")
else:
    print("✅ No old test data found")

# Step 3: Create test employees with different scenarios
print("\n[Step 3] Creating test employees...")

test_cases = [
    {
        "name": "Expires in 10 days",
        "days": 10,
        "should_send": True,
        "email": "test.visa.10days@example.com"
    },
    {
        "name": "Expires today",
        "days": 0,
        "should_send": True,
        "email": "test.visa.today@example.com"
    },
    {
        "name": "Expires in 30 days (boundary)",
        "days": 30,
        "should_send": True,
        "email": "test.visa.30days@example.com"
    },
    {
        "name": "Expires in 31 days (should NOT send)",
        "days": 31,
        "should_send": False,
        "email": "test.visa.31days@example.com"
    },
]

print(f"\nCreating {len(test_cases)} test employees:\n")

for i, test_case in enumerate(test_cases, 1):
    visa_date = date.today() + timedelta(days=test_case['days'])
    
    try:
        employee = Employee.objects.create(
            employee_first_name=f"Test{i}",
            employee_last_name=f"Visa{test_case['days']}Days",
            email=test_case['email'],
            phone=f"+123456789{i}",
            visa_expire_date=visa_date,
            is_active=True
        )
        
        status = "✅ Should send" if test_case['should_send'] else "❌ Should NOT send"
        print(f"{i}. {test_case['name']}")
        print(f"   Employee: {employee.get_full_name()}")
        print(f"   Email: {employee.email}")
        print(f"   Visa Date: {visa_date.strftime('%d %b %Y')}")
        print(f"   Email Status: {status}")
        print()
        
    except Exception as e:
        print(f"❌ Error creating employee: {e}\n")

# Step 4: Summary
print("=" * 70)
print("TEST COMPLETE!")
print("=" * 70)
print("\n📧 Check your email inbox(es) for:")
print("   - Admin emails (superuser emails)")
print("   - Employee emails (test.visa.*@example.com)")
print("\n📋 Expected emails:")
print("   - Test employees with visa expiring in 0-30 days: SHOULD receive email")
print("   - Test employee with visa expiring in 31 days: SHOULD NOT receive email")
print("\n💡 Tips:")
print("   - Check spam/junk folder if emails not in inbox")
print("   - Check Django console output for any errors")
print("   - Run 'python manage.py shell' and import EmailLog to check sent emails")
print("\n🎯 To view on dashboard:")
print("   - Navigate to Employee Dashboard")
print("   - Look for 'Visa Expiry' widget")
print("   - Click 'View all' to see full list")
print("\n" + "=" * 70)
