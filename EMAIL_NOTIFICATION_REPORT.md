# Email Notification System Report - Horilla HRMS

## Executive Summary

This report provides a comprehensive analysis of the email notification features in the Horilla HRMS system. The system has **extensive email and notification capabilities** for various HR operations including employee management, leave requests, payroll, attendance, recruitment, performance management, and more.

---

## 📧 Email Notification Features

### 1. **Visa Expiry Notifications** ✅

**Trigger:** When a new employee is created with a visa expiry date within 31 days

**Recipients:**
- **HR/Admin:** All superusers receive email notifications
- **Employee:** The employee whose visa is expiring receives an email

**Email Details:**
- **Admin Email Subject:** "Employee visa expiring: [Employee Name]"
- **Employee Email Subject:** "Your visa will expire soon"
- **Content:** Employee details, visa expiry date, days until expiry, action items
- **Templates:** 
  - `templates/emails/visa_expiry_admin_notification.html`
  - `templates/emails/visa_expiry_notification.html`

**Implementation:** `employee/signals.py` - `employee_post_save` signal

**Notification Window:** 0-30 days before expiry (31 days or more = no notification)

---

### 2. **Leave Management Notifications** ✅

**Scenarios:**

#### a) Leave Request Creation
- **Employee → Manager:** When employee creates a leave request
- **Notification Type:** In-app notification + Email (via automation)
- **Recipients:** Reporting manager or approval sequence managers
- **Message:** "You have a new leave request to validate"

#### b) Leave Request Approval
- **Manager → Employee:** When leave is approved
- **Recipients:** Employee who requested leave
- **Message:** Leave request approved notification

#### c) Leave Request Rejection
- **Manager → Employee:** When leave is rejected
- **Recipients:** Employee who requested leave
- **Message:** Leave request rejected notification

#### d) Leave Allocation Updates
- **HR → Employee:** When available leaves are updated
- **Recipients:** Affected employee
- **Message:** Available leaves updated notification

#### e) Compensatory Leave Requests
- **Employee → Manager:** Comp leave request notifications
- **Manager → Employee:** Approval/rejection notifications

**Implementation:** `leave/views.py` - Multiple notification points using `notify.send()`

---

### 3. **Attendance Notifications** ✅

**Scenarios:**

#### a) Attendance Validation
- **Manager → Employee:** When attendance is validated
- **Recipients:** Employee whose attendance was validated
- **Message:** Attendance validated notification

#### b) Attendance Request Approval/Rejection
- **Employee → Manager:** When attendance request is created
- **Manager → Employee:** When request is approved/rejected
- **Recipients:** Employee and reporting manager

#### c) Overtime Approval
- **Manager → Employee:** When overtime is approved
- **Recipients:** Employee
- **Message:** Overtime approved notification

**Implementation:** `attendance/views.py` and `attendance/views/requests.py`

---

### 4. **Payroll Notifications** ✅

**Scenarios:**

#### a) Payslip Generation
- **HR → Employee:** When payslip is created/saved
- **Recipients:** Employee
- **Message:** Payslip generated notification
- **Implementation:** `payroll/views/component_views.py`

#### b) Reimbursement Status
- **HR → Employee:** When reimbursement is approved/rejected
- **Recipients:** Employee and reporting manager
- **Message:** Reimbursement status update

#### c) Contract Updates
- **HR → Employee/Manager:** Contract-related notifications
- **Recipients:** Employee and reporting manager

**Implementation:** `payroll/views/views.py` and `payroll/views/component_views.py`

---

### 5. **Performance Management (PMS) Notifications** ✅

**Scenarios:**

#### a) Key Result Assignment
- **Manager → Employee:** When key results are assigned
- **Recipients:** Employee
- **Message:** Key result assigned notification

#### b) Objective Assignment
- **Manager → Employee:** When objectives are assigned
- **Recipients:** Employee
- **Message:** Objective assigned notification

#### c) Feedback Requests
- **Manager → Employee:** When feedback is requested
- **Recipients:** Employee and requested employees
- **Message:** Feedback request notification
- **Function:** `send_feedback_notifications()` in `pms/views.py`

#### d) Feedback Submission
- **Employee → Manager:** When feedback is submitted
- **Recipients:** Relevant employees and managers

**Implementation:** `pms/views.py` - Multiple notification points

---

### 6. **Recruitment Notifications** ✅

**Scenarios:**

#### a) Recruitment Manager Assignment
- **HR → Manager:** When assigned as recruitment manager
- **Recipients:** Assigned manager
- **Message:** Recruitment manager assignment notification

#### b) Recruitment Manager Removal
- **HR → Manager:** When removed as recruitment manager
- **Recipients:** Removed manager
- **Message:** Recruitment manager removal notification

#### c) Candidate Stage Updates
- **Manager → Manager:** Stage-related notifications
- **Recipients:** Stage managers

**Implementation:** `recruitment/views.py` and `recruitment/views/actions.py`

---

### 7. **Onboarding/Offboarding Notifications** ✅

**Scenarios:**

#### a) Onboarding Stage Creation
- **HR → Employee:** When new onboarding stage is created
- **Recipients:** Employees assigned to the stage
- **Message:** New onboarding stage notification

#### b) Onboarding Task Assignment
- **HR → Employee:** When tasks are assigned
- **Recipients:** Assigned employees
- **Message:** Task assignment notification

#### c) Task Updates
- **HR → Employee:** When tasks are updated
- **Recipients:** Assigned employees

**Implementation:** `onboarding/views.py`

---

### 8. **Asset Management Notifications** ✅

**Scenarios:**

#### a) Asset Assignment
- **HR → Employee:** When asset is assigned
- **Recipients:** Employee receiving the asset
- **Message:** Asset assignment notification

#### b) Asset Request Status
- **Employee → HR:** Asset request notifications
- **HR → Employee:** Request approval/rejection
- **Recipients:** Requesting employee and HR with permissions

#### c) Asset/Document Expiry Reminders
- **System → Employee/Admin:** Scheduled notifications for expiring assets/documents
- **Implementation:** `asset/scheduler.py`

**Implementation:** `asset/views.py` and `asset/scheduler.py`

---

### 9. **Project Management Notifications** ✅

**Scenarios:**

#### a) Project Status Updates
- **Manager → Team:** When project status changes
- **Recipients:** Project managers and members
- **Message:** Project status update notification

**Implementation:** `project/views.py`

---

### 10. **Automated Email System** ✅

**Feature:** Mail Automation Module

**Capabilities:**
- **Trigger-based emails:** On create, update, or delete of records
- **Customizable templates:** Using `HorillaMailTemplate` model
- **Delivery channels:** Email, In-app notification, or both
- **Conditional sending:** Based on field values and conditions
- **Attachments:** Support for template attachments
- **CC functionality:** Additional recipients via `also_sent_to` field

**Models:**
- `MailAutomation` - Defines automation rules
- `HorillaMailTemplate` - Email templates

**Implementation:** `horilla_automations/models.py` and `horilla_automations/signals.py`

**Supported Triggers:**
- `on_create` - When a record is created
- `on_update` - When a record is updated
- `on_delete` - When a record is deleted

---

## 🔔 Notification System Architecture

### In-App Notifications
- **Model:** `notifications/models.py` - `Notification` model
- **Signal:** `notify.send()` - Django signal for creating notifications
- **Features:**
  - Read/unread status
  - Notification levels (success, info, warning, error)
  - Multi-language support (English, Arabic, German, Spanish, French)
  - Soft delete capability
  - Email tracking (`emailed` field)

### Email Backend
- **Custom Backend:** `base/backends.py` - `DefaultHorillaMailBackend`
- **Features:**
  - Dynamic per-company SMTP configuration
  - Email logging via `EmailLog` model
  - Fallback to Django settings
  - Support for TLS/SSL
  - Robust error handling

### Email Configuration
- **Model:** `DynamicEmailConfiguration` - Per-company email settings
- **Email Log:** `EmailLog` - Tracks all sent emails
- **Templates:** HTML email templates in `templates/emails/`

---

## 📊 Summary Table

| Feature | Employee Notified | HR/Admin Notified | Email | In-App | Automation Support |
|---------|-------------------|-------------------|-------|--------|-------------------|
| Visa Expiry | ✅ | ✅ | ✅ | ❌ | ❌ |
| Leave Requests | ✅ | ✅ | ✅* | ✅ | ✅ |
| Leave Approval/Rejection | ✅ | ❌ | ✅* | ✅ | ✅ |
| Attendance Validation | ✅ | ❌ | ✅* | ✅ | ✅ |
| Attendance Requests | ✅ | ✅ | ✅* | ✅ | ✅ |
| Overtime Approval | ✅ | ❌ | ✅* | ✅ | ✅ |
| Payslip Generation | ✅ | ❌ | ✅* | ✅ | ✅ |
| Reimbursement Status | ✅ | ✅ | ✅* | ✅ | ✅ |
| Key Result Assignment | ✅ | ❌ | ✅* | ✅ | ✅ |
| Objective Assignment | ✅ | ❌ | ✅* | ✅ | ✅ |
| Feedback Requests | ✅ | ✅ | ✅* | ✅ | ✅ |
| Recruitment Manager Assignment | ❌ | ✅ | ✅* | ✅ | ✅ |
| Onboarding Tasks | ✅ | ❌ | ✅* | ✅ | ✅ |
| Asset Assignment | ✅ | ❌ | ✅* | ✅ | ✅ |
| Asset Request Status | ✅ | ✅ | ✅* | ✅ | ✅ |
| Asset/Document Expiry | ✅ | ✅ | ✅* | ✅ | ✅ |
| Project Status Updates | ✅ | ❌ | ✅* | ✅ | ✅ |

**Note:** ✅* = Email can be sent via Mail Automation system

---

## 🎯 Key Findings

### ✅ What Works Well

1. **Comprehensive Coverage:** The system covers virtually all HR operations
2. **Dual Notification System:** Both in-app notifications and emails
3. **Flexible Automation:** Mail automation system allows custom email workflows
4. **Multi-language Support:** Notifications support 5 languages
5. **Proper Separation:** Notifications for employees vs. HR/managers
6. **Email Logging:** All emails are tracked in `EmailLog`
7. **Graceful Failure:** Uses `fail_silently=True` and `contextlib.suppress(Exception)`
8. **Template System:** Professional HTML email templates

### 📋 Notification Recipients

**Employees receive notifications for:**
- Their own leave/attendance requests status
- Payslip generation
- Task assignments (onboarding, PMS)
- Asset assignments
- Visa expiry reminders
- Feedback requests
- Overtime approvals

**HR/Admins receive notifications for:**
- New leave/attendance requests
- Visa expiries (all employees)
- Asset requests
- Reimbursement requests
- Recruitment activities
- System-wide alerts

**Managers receive notifications for:**
- Team member requests (leave, attendance)
- Performance management activities
- Project updates
- Recruitment assignments

---

## 🔧 Technical Implementation

### Notification Flow
```
Action Triggered → notify.send() signal → 
→ Notification model created → 
→ In-app notification displayed → 
→ Optional: Email sent via automation
```

### Email Flow
```
Action Triggered → send_mail() or EmailMessage → 
→ DefaultHorillaMailBackend → 
→ SMTP server → 
→ EmailLog created → 
→ Email delivered
```

### Automation Flow
```
Model saved → post_save signal → 
→ Check MailAutomation rules → 
→ Evaluate conditions → 
→ Render template → 
→ Send email/notification → 
→ Log delivery
```

---

## 📝 Configuration Requirements

### Email Setup
1. Configure SMTP settings in `.env` or `settings.py`
2. Set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
3. Configure `DEFAULT_FROM_EMAIL`
4. Optional: Set up `DynamicEmailConfiguration` for per-company settings

### Notification Setup
1. Ensure `notifications` app is installed
2. Run migrations for notification models
3. Configure notification settings in `notifications/settings.py`

### Automation Setup
1. Create `HorillaMailTemplate` records for email templates
2. Create `MailAutomation` rules for automated emails
3. Configure trigger conditions and recipients

---

## 🚀 Recommendations

### For Administrators
1. **Set up superuser emails:** Ensure all superusers have valid email addresses
2. **Configure SMTP:** Properly configure email backend for production
3. **Create mail templates:** Design professional email templates for common scenarios
4. **Set up automations:** Configure mail automations for routine notifications
5. **Monitor email logs:** Regularly check `EmailLog` for delivery issues

### For Developers
1. **Use notify.send():** Consistently use the notification signal for in-app notifications
2. **Add email templates:** Create HTML templates for better user experience
3. **Handle exceptions:** Use `contextlib.suppress(Exception)` for non-critical notifications
4. **Test thoroughly:** Test email delivery in development and staging environments
5. **Document workflows:** Document notification workflows for maintenance

---

## 📚 Related Files

### Core Files
- `employee/signals.py` - Visa expiry email logic
- `notifications/signals.py` - Notification signal definition
- `notifications/base/models.py` - Notification model
- `base/backends.py` - Email backend
- `horilla_automations/models.py` - Mail automation models
- `horilla_automations/signals.py` - Automation signal handlers

### Email Templates
- `templates/emails/visa_expiry_admin_notification.html`
- `templates/emails/visa_expiry_notification.html`

### View Files with Notifications
- `leave/views.py`
- `attendance/views.py`
- `payroll/views/component_views.py`
- `payroll/views/views.py`
- `pms/views.py`
- `recruitment/views.py`
- `onboarding/views.py`
- `asset/views.py`
- `project/views.py`

---

## ✅ Conclusion

The Horilla HRMS system has a **robust and comprehensive email notification system** that covers all major HR operations. Both employees and HR/admins receive appropriate notifications for their respective actions and responsibilities. The system supports:

- ✅ Direct email notifications (visa expiry)
- ✅ In-app notifications (all operations)
- ✅ Automated email workflows (configurable)
- ✅ Multi-language support
- ✅ Email logging and tracking
- ✅ Flexible recipient configuration
- ✅ Professional HTML email templates

The notification system is well-architected, maintainable, and production-ready.

---

**Report Generated:** February 9, 2026  
**System:** Horilla HRMS  
**Analysis Scope:** Complete codebase email and notification features
