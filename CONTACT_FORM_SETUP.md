# Contact Form Setup Guide

## Overview

The contact form silently delivers emails to `minigolfeveryday@gmail.com` using the `/api/contact` endpoint.

## Features

- **Silent Delivery**: Emails sent directly to minigolfeveryday@gmail.com
- **Form Validation**: Client and server-side validation
- **Fallback Logging**: If email fails, submissions are logged to `contact_submissions.log`
- **Responsive Design**: Works on all devices
- **Success/Error Messages**: User-friendly feedback

## Environment Variables

Add these to your `.env` file for email functionality:

```bash
# Email Configuration (Optional - defaults to local mail server)
SMTP_SERVER=localhost
SMTP_PORT=25
SENDER_EMAIL=noreply@minigolfevery.day
SENDER_PASSWORD=

# For Gmail SMTP (if using Gmail as sender):
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SENDER_EMAIL=your-email@gmail.com
# SENDER_PASSWORD=your-app-password
```

## How It Works

1. **User submits form** → JavaScript sends POST to `/api/contact`
2. **Server validates** → Checks required fields and email format
3. **Email sent** → Uses SMTP to send to minigolfeveryday@gmail.com
4. **Fallback logging** → If email fails, logs to `contact_submissions.log`
5. **User feedback** → Shows success/error message

## Email Configuration Options

### Option 1: Local Mail Server (Default)
```bash
SMTP_SERVER=localhost
SMTP_PORT=25
```
Most shared hosting providers support this.

### Option 2: Gmail SMTP
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```
Requires Gmail app password setup.

### Option 3: Hosting Provider SMTP
```bash
SMTP_SERVER=mail.yourhostingprovider.com
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-smtp-password
```

## Testing

1. **Visit**: https://minigolfevery.day/contact.html
2. **Fill form** with test data
3. **Submit** and check for success message
4. **Check email** at minigolfeveryday@gmail.com
5. **Check logs** at `contact_submissions.log` if email fails

## Troubleshooting

### Email Not Sending
1. Check server logs for SMTP errors
2. Verify environment variables are set
3. Check hosting provider's SMTP settings
4. Look for submissions in `contact_submissions.log`

### Form Not Working
1. Check browser console for JavaScript errors
2. Verify `/api/contact` endpoint is accessible
3. Check server logs for API errors

## Security Features

- **Input Sanitization**: All inputs are cleaned and limited
- **Email Validation**: Proper email format checking
- **Rate Limiting**: Built into most hosting providers
- **CSRF Protection**: Standard web form protection

## Files Modified

- `contact.html` - New contact page
- `server.py` - Added `/api/contact` endpoint
- All navigation files - Added contact link
- `CONTACT_FORM_SETUP.md` - This guide

## Navigation Updates

Contact link added to:
- `index.html`
- `watch.html` 
- `blog.html`
- `about.html`
- `blog-admin.html` 