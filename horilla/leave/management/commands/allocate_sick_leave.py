from django.core.management.base import BaseCommand
from django.utils.timezone import now

from leave.models import LeaveType, AvailableLeave
from employee.models import Employee


class Command(BaseCommand):
    help = "Auto-allocate yearly Sick Leave to all active employees"

    def handle(self, *args, **kwargs):
        try:
            sick_leave = LeaveType.objects.get(name__iexact="Sick Leave")
        except LeaveType.DoesNotExist:
            self.stdout.write(self.style.ERROR("Sick Leave type not found"))
            return

        employees = Employee.objects.filter(is_active=True)
        created_count = 0

        for employee in employees:
            _, created = AvailableLeave.objects.get_or_create(
                employee_id=employee,
                leave_type_id=sick_leave,
                defaults={
                    "total_leave_days": 90,
                    "available_days": 90,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sick Leave allocated for {created_count} employees"
            )
        )
