import os
import smtplib
from email.message import EmailMessage
import logging

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
SHOW_EMAILS = os.getenv('SHOW_EMAILS', 'false').lower() in ('1','true','yes')

logger = logging.getLogger('healthcare.email')
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)


def send_email(to_email: str, subject: str, body: str):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        # SMTP not configured: if SHOW_EMAILS enabled, print to log; otherwise return False
        if SHOW_EMAILS:
            logger.info('DRY-RUN EMAIL to=%s subject=%s body="%s"', to_email, subject, body)
            return True
        logger.warning('SMTP not configured; email not sent to %s', to_email)
        return False
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)
    try:
        if SMTP_PORT == 465:
            s = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        else:
            s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
        s.quit()
        logger.info('Email sent to %s subject=%s', to_email, subject)
        return True
    except Exception:
        logger.exception('Failed to send email to %s', to_email)
        return False


def send_reset_email(to_email: str, token: str):
    reset_link = os.getenv("RESET_URL", f"http://localhost:8501/reset?token={token}")
    subject = "Password reset for Healthcare AI"
    body = f"Use the following link to reset your password (expires in 30 minutes):\n\n{reset_link}\n\nIf you did not request this, ignore this email."
    return send_email(to_email, subject, body)
