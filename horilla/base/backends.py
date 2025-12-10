"""
backends.py

Improved email backend for Horilla HRM.

Features:
- Dynamic per-company SMTP via DynamicEmailConfiguration (if present).
- Robust fallbacks to Django settings when no dynamic config / request exists.
- Logging of email sends to EmailLog (stores recipients as JSON string).
- make_email(...) factory to build EmailMessage safely (preferred to monkeypatching).
"""

import importlib
import json
import logging
from typing import Optional, Iterable

from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import render_to_string
from django.utils.module_loading import import_string

from base.models import DynamicEmailConfiguration, EmailLog
from horilla import settings
from horilla.horilla_middlewares import _thread_locals

logger = logging.getLogger(__name__)


class DefaultHorillaMailBackend(EmailBackend):
    """
    SMTP backend that will attempt to use a per-company DynamicEmailConfiguration
    (looked up from request thread-local). If none is found, falls back to Django settings.
    """

    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        use_tls=None,
        fail_silently=None,
        use_ssl=None,
        timeout=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        **kwargs,
    ):
        # Resolve configuration from DB if possible. This function is safe if called
        # with no request (management commands, Celery workers).
        try:
            self.configuration = self.get_dynamic_email_config()
        except Exception:
            # Any exception when resolving DB config should not break init.
            logger.exception("Failed to load dynamic email configuration; falling back to settings.")
            self.configuration = None

        ssl_keyfile = (
            getattr(self.configuration, "ssl_keyfile", None)
            if self.configuration
            else ssl_keyfile or getattr(settings, "ssl_keyfile", None)
        )
        ssl_certfile = (
            getattr(self.configuration, "ssl_certfile", None)
            if self.configuration
            else ssl_certfile or getattr(settings, "ssl_certfile", None)
        )

        # Prepare values resolved from configuration or settings
        resolved_host = self.dynamic_host
        resolved_port = self.dynamic_port
        resolved_username = self.dynamic_username
        resolved_password = self.dynamic_password
        resolved_use_tls = self.dynamic_use_tls
        resolved_fail_silently = self.dynamic_fail_silently
        resolved_use_ssl = self.dynamic_use_ssl
        resolved_timeout = self.dynamic_timeout

        # Call parent init with resolved values.
        # EmailBackend signature accepts these keyword args in Django stable releases.
        super().__init__(
            host=resolved_host,
            port=resolved_port,
            username=resolved_username,
            password=resolved_password,
            use_tls=resolved_use_tls,
            fail_silently=resolved_fail_silently,
            use_ssl=resolved_use_ssl,
            timeout=resolved_timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            **kwargs,
        )

    @staticmethod
    def get_dynamic_email_config() -> Optional[DynamicEmailConfiguration]:
        """
        Try to load DynamicEmailConfiguration for the current request/company.
        Return None if not available.
        """
        request = getattr(_thread_locals, "request", None)
        company = None
        try:
            if request and getattr(request, "user", None) and not request.user.is_anonymous:
                # adjust to your actual method to fetch company from user
                company = request.user.employee_get.get_company()
        except Exception:
            # don't fail the whole lookup if user object shape is unexpected
            logger.debug("Could not determine company from request user.", exc_info=True)
            company = None

        try:
            configuration = (
                DynamicEmailConfiguration.objects.filter(company_id=company).first()
            )
            if configuration is None:
                configuration = DynamicEmailConfiguration.objects.filter(is_primary=True).first()
        except Exception:
            # DB not available or model error
            logger.exception("Error querying DynamicEmailConfiguration.")
            configuration = None

        # If configuration found, prepare caching of display name/reply_to for request user
        if configuration:
            try:
                display_email_name = f"{configuration.display_name} <{configuration.from_email}>"
                user_id = ""
                if request and getattr(request, "user", None) and request.user.is_authenticated:
                    if getattr(configuration, "use_dynamic_display_name", False):
                        # if enabled, display from user's full name + email
                        display_email_name = f"{request.user.employee_get.get_full_name()} <{request.user.employee_get.get_email()}>"
                    user_id = request.user.pk
                    reply_to = [
                        f"{request.user.employee_get.get_full_name()} <{request.user.employee_get.get_email()}>"
                    ]
                    cache.set(f"reply_to{request.user.pk}", reply_to)
                cache.set(f"dynamic_display_name{user_id}", display_email_name)
            except Exception:
                logger.exception("Failed to cache dynamic display name/reply_to.")

        return configuration

    # dynamic property accessors with safe fallbacks to settings
    @property
    def dynamic_host(self):
        return getattr(self.configuration, "host", None) if self.configuration else getattr(settings, "EMAIL_HOST", None)

    @property
    def dynamic_port(self):
        return getattr(self.configuration, "port", None) if self.configuration else getattr(settings, "EMAIL_PORT", None)

    @property
    def dynamic_username(self):
        return getattr(self.configuration, "username", None) if self.configuration else getattr(settings, "EMAIL_HOST_USER", None)

    @property
    def dynamic_mail_sent_from(self):
        return getattr(self.configuration, "from_email", None) if self.configuration else getattr(settings, "DEFAULT_FROM_EMAIL", None)

    @property
    def dynamic_display_name(self):
        return getattr(self.configuration, "display_name", None) if self.configuration else None

    @property
    def dynamic_from_email_with_display_name(self):
        if self.dynamic_display_name:
            return f"{self.dynamic_display_name} <{self.dynamic_mail_sent_from}>"
        return self.dynamic_mail_sent_from

    @property
    def dynamic_password(self):
        return getattr(self.configuration, "password", None) if self.configuration else getattr(settings, "EMAIL_HOST_PASSWORD", None)

    @property
    def dynamic_use_tls(self):
        return getattr(self.configuration, "use_tls", None) if self.configuration else getattr(settings, "EMAIL_USE_TLS", None)

    @property
    def dynamic_fail_silently(self):
        return getattr(self.configuration, "fail_silently", None) if self.configuration else getattr(settings, "EMAIL_FAIL_SILENTLY", True)

    @property
    def dynamic_use_ssl(self):
        return getattr(self.configuration, "use_ssl", None) if self.configuration else getattr(settings, "EMAIL_USE_SSL", None)

    @property
    def dynamic_timeout(self):
        return getattr(self.configuration, "timeout", None) if self.configuration else getattr(settings, "EMAIL_TIMEOUT", None)


# Resolve configured backend class (respect settings EMAIL_BACKEND if it points elsewhere)
EMAIL_BACKEND_PATH = getattr(settings, "EMAIL_BACKEND", "")
BACKEND_CLASS = DefaultHorillaMailBackend
DEFAULT_BACKEND_PATH = "base.backends.ConfiguredEmailBackend"

if EMAIL_BACKEND_PATH and EMAIL_BACKEND_PATH != DEFAULT_BACKEND_PATH:
    try:
        module_path, class_name = EMAIL_BACKEND_PATH.rsplit(".", 1)
        module = importlib.import_module(module_path)
        BACKEND_CLASS = getattr(module, class_name)
    except Exception:
        logger.exception("Failed to import EMAIL_BACKEND from settings; falling back to DefaultHorillaMailBackend.")
        BACKEND_CLASS = DefaultHorillaMailBackend


class ConfiguredEmailBackend(BACKEND_CLASS):
    """
    Concrete backend used by Django when EMAIL_BACKEND references this module.
    It delegates sending to the parent backend and logs attempts to EmailLog.
    """

    def send_messages(self, email_messages: Optional[Iterable[EmailMessage]]):
        """Call parent send_messages and create EmailLog entries for each message.
        On exception capture the traceback and save it into EmailLog.error_message.
        Returns the same numeric response the parent backend returns (count of sent messages)."""
        import traceback
        import json
        from base.models import EmailLog
        from django.conf import settings

        try:
            # call parent backend (this may raise)
            response = super(ConfiguredEmailBackend, self).send_messages(email_messages)
            sent_flag = bool(response)
            exception_text = None
        except Exception:
            # capture full traceback for logging and saving to EmailLog
            logger.exception("Error while sending messages in backend.")
            exception_text = traceback.format_exc()
            response = 0
            sent_flag = False

        # Create an EmailLog entry for each message (include traceback if failed)
        for message in email_messages or []:
            try:
                EmailLog.objects.create(
                    subject=message.subject or "",
                    body=(message.body or "")[:4000],
                    from_email=(
                        getattr(self, "dynamic_from_email_with_display_name", None)
                        or getattr(settings, "DEFAULT_FROM_EMAIL", "")
                    ),
                    to=json.dumps(message.to) if isinstance(message.to, (list, tuple)) else (message.to or ""),
                    status="sent" if sent_flag else "failed",
                    error_message=exception_text,
                )
            except Exception:
                # ensure logging failures don't break email sending flow
                logger.exception("Failed to write EmailLog entry.")

        return response



__all__ = ["ConfiguredEmailBackend", "DefaultHorillaMailBackend", "make_email"]


# -------------------------
# Helper: safe factory
# -------------------------
def make_email(
    subject: str = "",
    template_name: Optional[str] = None,
    context: Optional[dict] = None,
    plain_message: Optional[str] = None,
    from_email: Optional[str] = None,
    to: Optional[Iterable[str]] = None,
    reply_to: Optional[Iterable[str]] = None,
    cc: Optional[Iterable[str]] = None,
    bcc: Optional[Iterable[str]] = None,
    attachments: Optional[Iterable] = None,
) -> EmailMessage:
    """
    Construct an EmailMessage with dynamic 'from_email' and 'reply_to' lookups.
    Use this helper instead of monkeypatching EmailMessage.__init__ globally.
    If template_name is provided and context is provided, the rendered template is used as HTML body.
    """
    request = getattr(_thread_locals, "request", None)
    user_id = ""
    try:
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            user_id = request.user.pk
            # cached reply_to if previously stored by get_dynamic_email_config
            reply_to = reply_to or cache.get(f"reply_to{user_id}")
    except Exception:
        logger.debug("Could not obtain request/user for dynamic reply_to.", exc_info=True)

    if not from_email:
        from_email = cache.get(f"dynamic_display_name{user_id}") or getattr(settings, "DEFAULT_FROM_EMAIL", None)

    body = plain_message or ""
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=list(to) if to else None,
        cc=list(cc) if cc else None,
        bcc=list(bcc) if bcc else None,
        reply_to=list(reply_to) if reply_to else None,
        attachments=attachments,
    )

    # Render template if requested
    if template_name and context is not None:
        try:
            html = render_to_string(template_name, context)
            msg.body = html
            msg.content_subtype = "html"
        except Exception:
            logger.exception("Failed to render email template; falling back to plain body.")

    return msg
