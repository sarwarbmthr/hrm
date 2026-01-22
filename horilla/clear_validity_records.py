#!/usr/bin/env python
"""
Script to delete all validity records from database
Run with: python manage.py shell < clear_validity_records.py
"""
from employee.models import ValidityRecord

# Delete all records
count = ValidityRecord.objects.all().count()
print(f"Found {count} validity records")

if count > 0:
    ValidityRecord.objects.all().delete()
    print("✓ All validity records deleted successfully!")
else:
    print("✓ No records to delete - table is already empty")

# Verify
remaining = ValidityRecord.objects.all().count()
print(f"Remaining records: {remaining}")
