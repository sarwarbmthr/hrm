"""
Test Payslip Email - Run in Django shell
python manage.py shell < test_payslip_email.py
"""

from payroll.models.models import Payslip
from employee.models import Employee

print("=" * 80)
print("TESTING PAYSLIP EMAIL ISSUE")
print("=" * 80)

# Check payslips
print("\n[1] Checking Payslips...")
payslips = Payslip.objects.all().order_by('-id')[:5]

if not payslips.exists():
    print("❌ NO PAYSLIPS FOUND!")
    print("   Create some payslips first")
else:
    print(f"✅ Found {payslips.count()} recent payslips\n")
    
    for payslip in payslips:
        print(f"Payslip ID: {payslip.id}")
        print(f"  Employee: {payslip.employee_id.get_full_name()}")
        
        # Check employee email
        try:
            emp_email = payslip.employee_id.get_mail()
            if emp_email:
                print(f"  ✅ Email: {emp_email}")
            else:
                print(f"  ❌ NO EMAIL ADDRESS!")
                print(f"     This employee won't receive emails!")
        except Exception as e:
            print(f"  ❌ ERROR getting email: {e}")
        
        # Check sent status
        if payslip.sent_to_employee:
            print(f"  ✅ Status: Already sent")
        else:
            print(f"  ⏳ Status: Not sent yet")
        
        print("-" * 80)

# Check employees without email
print("\n[2] Checking Employees Without Email...")
employees_no_email = []

for emp in Employee.objects.filter(is_active=True):
    try:
        email = emp.get_mail()
        if not email:
            employees_no_email.append(emp)
    except:
        employees_no_email.append(emp)

if employees_no_email:
    print(f"⚠️  WARNING: {len(employees_no_email)} employees have NO email!")
    print("\nEmployees without email:")
    for emp in employees_no_email[:10]:
        print(f"   - {emp.get_full_name()}")
    if len(employees_no_email) > 10:
        print(f"   ... and {len(employees_no_email) - 10} more")
else:
    print("✅ All active employees have email addresses")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)

if employees_no_email:
    print("\n1. Add email addresses to employees:")
    print("   - Go to Employee → Employee List")
    print("   - Edit each employee")
    print("   - Add email in 'Work Email' or 'Email' field")
    
print("\n2. Watch Django console when sending payslip:")
print("   - Look for errors in the terminal where Django is running")
print("   - Errors will show there, not in the browser")

print("\n3. Check if thread is failing:")
print("   - The email sending happens in background thread")
print("   - If thread fails, you won't see error in browser")
print("   - Check Django console output")

print("\n" + "=" * 80)
