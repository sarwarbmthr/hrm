"""
Diagnostic Script for Payslip Email Issues
Run this in Django shell: python manage.py shell < DIAGNOSE_PAYSLIP_EMAIL_ISSUE.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from base.backends import ConfiguredEmailBackend
from employee.models import Employee
from payroll.models.models import Payslip

print("=" * 80)
print("PAYSLIP EMAIL DIAGNOSTIC TOOL")
print("=" * 80)

# Test 1: Check Email Configuration
print("\n[Test 1] Checking Email Configuration...")
print("-" * 80)

try:
    email_backend = ConfiguredEmailBackend()
    print(f"✅ Email Backend: {settings.EMAIL_BACKEND}")
    print(f"✅ Email Host: {settings.EMAIL_HOST}")
    print(f"✅ Email Port: {settings.EMAIL_PORT}")
    print(f"✅ Email User: {settings.EMAIL_HOST_USER}")
    print(f"✅ Email Use TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
    print(f"✅ Email Use SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    print(f"✅ Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # Check dynamic email config
    display_name = getattr(email_backend, "dynamic_from_email_with_display_name", None)
    if display_name:
        print(f"✅ Dynamic From Email: {display_name}")
    else:
        print("⚠️  WARNING: No dynamic_from_email_with_display_name found")
        print("   This might cause the 'Email server is not configured' error")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Check Employee Email Addresses
print("\n[Test 2] Checking Employee Email Addresses...")
print("-" * 80)

try:
    employees = Employee.objects.filter(is_active=True)[:10]
    print(f"Total Active Employees: {Employee.objects.filter(is_active=True).count()}")
    print(f"\nChecking first 10 employees:")
    
    for emp in employees:
        try:
            email = emp.get_mail() if hasattr(emp, 'get_mail') else emp.email
            status = "✅" if email else "❌ NO EMAIL"
            print(f"   {status} {emp.get_full_name()}: {email}")
        except Exception as e:
            print(f"   ❌ {emp.get_full_name()}: ERROR - {e}")
            
    # Count employees without email
    no_email_count = 0
    for emp in Employee.objects.filter(is_active=True):
        try:
            email = emp.get_mail() if hasattr(emp, 'get_mail') else emp.email
            if not email:
                no_email_count += 1
        except:
            no_email_count += 1
    
    if no_email_count > 0:
        print(f"\n⚠️  WARNING: {no_email_count} employees have no email address!")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Check Recent Payslips
print("\n[Test 3] Checking Recent Payslips...")
print("-" * 80)

try:
    payslips = Payslip.objects.all().order_by('-id')[:5]
    print(f"Total Payslips: {Payslip.objects.count()}")
    print(f"\nRecent 5 payslips:")
    
    for payslip in payslips:
        sent_status = "✅ SENT" if payslip.sent_to_employee else "❌ NOT SENT"
        try:
            emp_email = payslip.employee_id.get_mail() if hasattr(payslip.employee_id, 'get_mail') else payslip.employee_id.email
            email_status = f"Email: {emp_email}" if emp_email else "⚠️  NO EMAIL"
        except:
            email_status = "⚠️  ERROR getting email"
            
        print(f"   {sent_status} | {payslip.employee_id.get_full_name()} | {email_status}")
        print(f"      Period: {payslip.start_date} to {payslip.end_date} | Status: {payslip.status}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Test Email Sending
print("\n[Test 4] Testing Email Sending...")
print("-" * 80)

test_email = input("Enter your test email address (or press Enter to skip): ").strip()

if test_email:
    try:
        print(f"Attempting to send test email to: {test_email}")
        
        send_mail(
            subject='Horilla Payslip Email Test',
            message='This is a test email from Horilla HRMS. If you receive this, email configuration is working!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        print("✅ Test email sent successfully!")
        print("   Check your inbox (and spam folder)")
        
    except Exception as e:
        print(f"❌ ERROR sending test email: {e}")
        print("\nPossible issues:")
        print("   1. SMTP credentials are incorrect")
        print("   2. Gmail 'Less secure app access' is disabled")
        print("   3. Need to use App Password instead of regular password")
        print("   4. Firewall blocking SMTP port")
        print("   5. Email server is down")
else:
    print("⏭️  Skipped email sending test")

# Test 5: Check Django Logs
print("\n[Test 5] Checking for Email Errors in Logs...")
print("-" * 80)

try:
    from base.models import EmailLog
    
    recent_logs = EmailLog.objects.all().order_by('-id')[:5]
    
    if recent_logs.exists():
        print(f"Recent {recent_logs.count()} email logs:")
        for log in recent_logs:
            status_icon = "✅" if log.status == "sent" else "❌"
            print(f"   {status_icon} {log.subject} | To: {log.to} | Status: {log.status}")
            if log.error_message:
                print(f"      Error: {log.error_message[:100]}...")
    else:
        print("⚠️  No email logs found in database")
        print("   This might mean emails are not being logged or no emails have been sent")
        
except Exception as e:
    print(f"⚠️  Could not check EmailLog: {e}")

# Test 6: Check Thread Execution
print("\n[Test 6] Checking Thread Execution...")
print("-" * 80)

print("The email sending uses threading (MailSendThread)")
print("If emails are not being sent, possible issues:")
print("   1. Thread is starting but failing silently")
print("   2. Exception in thread is being caught and logged")
print("   3. Check Django console/logs for exceptions")
print("\nTo debug further:")
print("   1. Check Django console output when clicking 'Send via mail'")
print("   2. Look for exceptions in logs")
print("   3. Check if thread is actually starting")

# Summary
print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

print("\n✅ CHECKS TO VERIFY:")
print("   1. Email configuration is correct in .env")
print("   2. Employees have valid email addresses")
print("   3. Test email can be sent successfully")
print("   4. Check EmailLog for errors")
print("   5. Check Django console for thread exceptions")

print("\n⚠️  COMMON ISSUES:")
print("   1. Gmail requires 'App Password' not regular password")
print("   2. 'Less secure app access' must be enabled (or use App Password)")
print("   3. Employee email field is empty or invalid")
print("   4. SMTP port blocked by firewall")
print("   5. Thread exception being silently caught")

print("\n🔧 NEXT STEPS:")
print("   1. If test email works: Check employee email addresses")
print("   2. If test email fails: Fix SMTP configuration")
print("   3. Check Django console when sending payslip emails")
print("   4. Enable DEBUG=True to see detailed errors")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
