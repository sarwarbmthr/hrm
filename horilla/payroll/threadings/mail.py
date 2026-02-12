"""
mail.py

This module is used handle mail sent in thread
"""

import logging
from threading import Thread

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from base.backends import ConfiguredEmailBackend
from employee.models import EmployeeWorkInformation
from payroll.models.models import Payslip
from payroll.views.views import payslip_pdf

logger = logging.getLogger(__name__)


class MailSendThread(Thread):
    """
    MailSend
    """

    def __init__(self, request, result_dict, ids):
        Thread.__init__(self)
        self.result_dict = result_dict
        self.ids = ids
        self.request = request
        self.host = request.get_host()
        self.protocol = "https" if request.is_secure() else "http"

    def run(self) -> None:
        super().run()
        for record in list(self.result_dict.values()):
            try:
                html_message = render_to_string(
                    "payroll/mail_templates/default.html",
                    {
                        "record": record,
                        "host": self.host,
                        "protocol": self.protocol,
                    },
                    request=self.request,
                )
                attachments = []
                for instance in record["instances"]:
                    response = payslip_pdf(self.request, instance.id)
                    attachments.append(
                        (
                            f"{instance.get_payslip_title()}.pdf",
                            response.content,
                            "application/pdf",
                        )
                    )
                employee = record["instances"][0].employee_id
                employee_email = employee.get_mail()
                
                # Check if employee has email
                if not employee_email:
                    logger.error(f"❌ Cannot send email: Employee {employee.get_full_name()} has no email address!")
                    continue
                
                logger.info(f"📧 Preparing to send payslip email to: {employee.get_full_name()} ({employee_email})")
                
                email_backend = ConfiguredEmailBackend()
                display_email_name = email_backend.dynamic_from_email_with_display_name
                if self.request:
                    try:
                        display_email_name = f"{self.request.user.employee_get.get_full_name()} <{self.request.user.employee_get.email}>"
                    except:
                        logger.error(Exception)

                email = EmailMessage(
                    f"Hello, {record['instances'][0].get_name()} Your Payslips is Ready!",
                    html_message,
                    display_email_name,
                    [employee_email],
                    reply_to=[display_email_name],
                )
                email.attachments = attachments

                # Send the email
                email.content_subtype = "html"
                try:
                    email.send()
                    Payslip.objects.filter(id__in=self.ids).update(sent_to_employee=True)
                    logger.info(f"✅ Email sent successfully to: {employee.get_full_name()} ({employee_email})")
                except Exception as e:
                    logger.exception(f"❌ Failed to send email to {employee.get_full_name()} ({employee_email}): {e}")
                    
            except Exception as e:
                logger.exception(f"❌ Error in email thread: {e}")

        return
