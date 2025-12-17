from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Employee


@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance: Employee, created, **kwargs):
    """When a new Employee is created, if their visa expires within 31 days
    send notification emails to admins and the employee.
    """
    if not created:
        return

    if not instance.visa_expire_date:
        return

    days = (instance.visa_expire_date - date.today()).days
    # only notify for upcoming expiries within 31 days (including today)
    if days < 0 or days > 30:
        return

    # Prepare admin recipients (superusers)
    admin_emails = list(
        User.objects.filter(is_superuser=True).values_list("email", flat=True)
    )

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(
        settings, "EMAIL_HOST_USER", None
    )
    if not from_email:
        from_email = "no-reply@localhost"

    # Send admin summary (reuse template if present)
    if admin_emails:
        subject_admin = f"Employee visa expiring: {instance.get_full_name()}"
        try:
            body_admin = render_to_string(
                "emails/visa_expiry_admin_notification.html",
                {"employees": [instance], "days": days},
            )
            send_mail(
                subject_admin,
                body_admin,
                from_email,
                admin_emails,
                html_message=body_admin,
                fail_silently=True,
            )
        except Exception:
            # Fallback plain text
            body = (
                f"Employee {instance.get_full_name()} has visa expiring on "
                f"{instance.visa_expire_date} ({days} days remaining)."
            )
            send_mail(subject_admin, body, from_email, admin_emails, fail_silently=True)

    # Send notification to employee
    try:
        emp_email = instance.get_email() if hasattr(instance, "get_email") else instance.email
    except Exception:
        emp_email = getattr(instance, "email", None)

    if emp_email:
        subject_emp = "Your visa will expire soon"
        try:
            body_emp = render_to_string(
                "emails/visa_expiry_notification.html",
                {"employee": instance, "days": days},
            )
            send_mail(
                subject_emp,
                body_emp,
                from_email,
                [emp_email],
                html_message=body_emp,
                fail_silently=True,
            )
        except Exception:
            send_mail(
                subject_emp,
                f"Your visa expires on {instance.visa_expire_date} ({days} days).",
                from_email,
                [emp_email],
                fail_silently=True,
            )
