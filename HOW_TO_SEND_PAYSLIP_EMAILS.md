# How to Send Payslip Emails to Employees - Step-by-Step Guide

## Overview
After generating payslips, HR/Admin needs to manually send emails to employees. This is a **separate action** from payslip generation.

---

## Method 1: Bulk Send Emails (Multiple Employees)

### Step-by-Step Instructions:

#### **Step 1: Navigate to Payslip View**
1. Login as HR/Admin
2. Go to **Payroll** menu
3. Click on **Payslip** or **View Payslips**
4. URL: `/payroll/view-payslip`

#### **Step 2: Select Payslips to Email**
1. You'll see a list of all generated payslips
2. **Check the checkboxes** next to the payslips you want to email
3. You can select:
   - Individual payslips (one by one)
   - Multiple payslips (select all you want)
   - All payslips on the page

**Visual Indicator:**
- Payslips already sent will have a **green/yellowgreen button** (sent_to_employee)
- Payslips not yet sent will have a **light background button**

#### **Step 3: Click "Actions" Dropdown**
1. Look for the **"Actions"** button at the top of the page
2. Click on it to open the dropdown menu

#### **Step 4: Click "Send via mail"**
1. In the Actions dropdown, find **"Send via mail"** option
2. Click on it
3. A confirmation message will appear: **"Mail processing"**

#### **Step 5: Verify Email Sent**
1. The system will process emails in the background
2. You'll see a message: **"Mail processing"**
3. The mail icon button will turn **green** (yellowgreen background)
4. Database field `sent_to_employee` will be set to `True`

---

## Method 2: Send Individual Payslip Email (Single Employee)

### Step-by-Step Instructions:

#### **Option A: From Payslip List View**

1. Navigate to **Payroll → Payslip**
2. Find the employee's payslip in the list
3. Look for the **mail icon** button (📧) next to each payslip
4. Click the **mail icon button**
5. Confirm: **"Do you want to send the payslip by mail?"**
6. Click **Yes/OK**
7. Email will be sent immediately

#### **Option B: From Individual Payslip View**

1. Navigate to **Payroll → Payslip**
2. Click on a specific payslip to view details
3. Look for the **mail icon** button (📧) at the top
4. Click the **mail icon button**
5. Confirm: **"Do you want to send the payslip by mail?"**
6. Click **Yes/OK**
7. Email will be sent immediately

---

## What Happens When Email is Sent?

### Email Content:
- **Subject:** "Hello, [Employee Name] Your Payslips is Ready!"
- **Body:** HTML formatted email with payslip details
- **Attachment:** Payslip PDF file(s)
- **From:** HR's email (or configured email)
- **To:** Employee's email address

### Email Template Location:
`horilla/payroll/templates/payroll/mail_templates/default.html`

### Technical Process:
1. System creates email with HTML content
2. Generates PDF of payslip(s)
3. Attaches PDF to email
4. Sends email via configured SMTP server
5. Updates database: `sent_to_employee = True`
6. Changes button color to green

---

## Visual Guide

### Payslip List View:

```
┌─────────────────────────────────────────────────────────────┐
│  Payroll > Payslip                                          │
├─────────────────────────────────────────────────────────────┤
│  [Search] [Filter] [Group By] [Actions ▼]                  │
│                                                              │
│  Actions Dropdown:                                          │
│  ┌──────────────────────┐                                   │
│  │ ✓ Generate           │                                   │
│  │ ✓ Payslip report     │                                   │
│  │ ✓ Send via mail  ←── CLICK HERE FOR BULK SEND          │
│  │ ✓ Bulk Status Update │                                   │
│  │ ✓ Export             │                                   │
│  └──────────────────────┘                                   │
│                                                              │
│  ☐ Employee Name | Period | Status | Actions                │
│  ☐ John Doe     | Jan 2026 | Draft | [📧] [👁] [✏️] [🗑]  │
│  ☐ Jane Smith   | Jan 2026 | Draft | [📧] [👁] [✏️] [🗑]  │
│  ☐ Bob Johnson  | Jan 2026 | Draft | [📧] [👁] [✏️] [🗑]  │
│                                      ↑                       │
│                                      └─ Click mail icon      │
│                                         for individual send  │
└─────────────────────────────────────────────────────────────┘
```

### Button States:

**Before Sending:**
```
[📧]  ← Light background (oh-btn--light-bkg)
```

**After Sending:**
```
[📧]  ← Green background (sent-to-employee class)
```

---

## Important Notes

### ✅ **What Works:**
- Bulk sending to multiple employees at once
- Individual sending per employee
- Email includes PDF attachment
- Multi-language support
- Confirmation dialog before sending

### ⚠️ **Important Points:**
1. **Email must be sent manually** - It does NOT happen automatically during payslip generation
2. **Email server must be configured** - Check `.env` file for SMTP settings
3. **Employees must have email addresses** - System uses `employee.get_mail()`
4. **Can send multiple times** - No restriction on re-sending
5. **Background processing** - Emails are sent in a separate thread

### ❌ **Common Issues:**

**Issue 1: "Email server is not configured"**
- **Solution:** Configure SMTP settings in `.env` or database
- Check `DynamicEmailConfiguration` model
- Verify `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

**Issue 2: Emails not received**
- Check employee email addresses are valid
- Check spam/junk folder
- Check email server logs
- Verify SMTP credentials

**Issue 3: Button doesn't appear**
- Check user has permission: `payroll.add_payslip`
- Ensure payslips exist in the list

---

## URL Endpoints

### Bulk Send:
- **URL:** `/payroll/send-slip`
- **Method:** GET
- **Parameters:** `id` (list of payslip IDs)
- **Example:** `/payroll/send-slip?id=1&id=2&id=3`

### Individual Send:
- **URL:** `/payroll/send-slip`
- **Method:** GET
- **Parameters:** `id` (single payslip ID), `view` (optional)
- **Example:** `/payroll/send-slip?id=5&view=individual-payslip`

---

## Code Reference

### View Function:
**File:** `horilla/payroll/views/component_views.py`
**Function:** `send_slip()` (Line 1203)

### Email Thread:
**File:** `horilla/payroll/threadings/mail.py`
**Class:** `MailSendThread` (Line 21)

### Templates:
- **Payslip List:** `horilla/payroll/templates/payroll/payslip/view_payslips.html`
- **Email Template:** `horilla/payroll/templates/payroll/mail_templates/default.html`

### URL Pattern:
**File:** `horilla/payroll/urls/component_urls.py`
```python
path("send-slip", component_views.send_slip, name="send-slip"),
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PAYSLIP EMAIL WORKFLOW                    │
└─────────────────────────────────────────────────────────────┘

Step 1: Generate Payslips
    ↓
    HR generates payslips for employees
    ↓
    Payslips saved with status="draft"
    ↓
    Employees receive IN-APP notification
    ↓
    ❌ NO EMAIL SENT YET

Step 2: Send Emails (Manual Action)
    ↓
    HR navigates to Payroll → Payslip
    ↓
    HR selects payslips (checkboxes)
    ↓
    HR clicks Actions → "Send via mail"
    ↓
    System confirms: "Mail processing"
    ↓
    MailSendThread starts
    ↓
    For each employee:
        - Render HTML email
        - Generate PDF attachment
        - Send email
        - Update sent_to_employee=True
    ↓
    ✅ Employees receive EMAIL with PDF

Step 3: Verification
    ↓
    Mail icon turns GREEN
    ↓
    Employee checks email inbox
    ↓
    Employee downloads PDF attachment
    ↓
    ✅ COMPLETE
```

---

## Quick Reference Card

| Action | Location | Button/Link | Result |
|--------|----------|-------------|--------|
| **Bulk Send** | Payroll → Payslip | Actions → "Send via mail" | Emails all selected payslips |
| **Individual Send** | Payslip list row | 📧 Mail icon | Emails single payslip |
| **Individual Send** | Payslip detail view | 📧 Mail icon (top) | Emails single payslip |
| **Check Status** | Payslip list | Button color | Green = sent, Light = not sent |

---

## Permissions Required

To send payslip emails, the user must have:
- **Permission:** `payroll.add_payslip`
- **Role:** HR, Admin, or Payroll Manager

---

## Testing Steps

### Test Bulk Email Sending:

1. **Generate test payslips:**
   ```
   Payroll → Generate Payslip
   Select 3-5 employees
   Generate
   ```

2. **Send emails:**
   ```
   Payroll → Payslip
   Check all payslips
   Actions → Send via mail
   Confirm
   ```

3. **Verify:**
   ```
   - Check "Mail processing" message appears
   - Check mail icons turn green
   - Check employee email inboxes
   - Verify PDF attachments received
   ```

### Test Individual Email Sending:

1. **Navigate to payslip:**
   ```
   Payroll → Payslip
   Find one payslip
   ```

2. **Send email:**
   ```
   Click 📧 mail icon
   Confirm dialog
   ```

3. **Verify:**
   ```
   - Check mail icon turns green
   - Check employee email inbox
   - Verify PDF attachment
   ```

---

## Troubleshooting

### Problem: "No rows are selected for sending payslips"
**Solution:** Select at least one payslip checkbox before clicking "Send via mail"

### Problem: "Email server is not configured"
**Solution:** 
1. Check `.env` file has email settings
2. Verify `DynamicEmailConfiguration` in database
3. Test email connection

### Problem: Emails sent but not received
**Solution:**
1. Check employee email addresses in database
2. Check spam/junk folders
3. Check email server logs
4. Verify SMTP credentials are correct

### Problem: Mail icon doesn't turn green
**Solution:**
1. Check browser console for errors
2. Refresh the page
3. Check database: `sent_to_employee` field
4. Check email actually sent (check logs)

---

## Summary

**To send payslip emails to employees:**

1. ✅ Generate payslips first
2. ✅ Navigate to **Payroll → Payslip**
3. ✅ Select payslips (checkboxes)
4. ✅ Click **Actions → "Send via mail"**
5. ✅ Confirm and wait for "Mail processing"
6. ✅ Verify green mail icons
7. ✅ Employees receive emails with PDF

**Remember:** Email sending is a **separate manual action** after payslip generation!

---

**Document Version:** 1.0  
**Last Updated:** February 9, 2026  
**System:** Horilla HRMS Payroll Module
