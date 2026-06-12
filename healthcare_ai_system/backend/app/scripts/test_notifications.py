import os
import sys
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, proj_root)
from backend.app import email_utils, sms_utils

print('SHOW_EMAILS default:', os.getenv('SHOW_EMAILS'))
print('Sending reset email (dry-run if SMTP not configured)')
res = email_utils.send_reset_email('test@example.com', 'dummy-token')
print('send_reset_email returned', res)

print('\nSending SMS (dry-run if TWILIO not configured)')
res2 = sms_utils.send_sms('+15551234567', 'Test message from Healthcare AI')
print('send_sms returned', res2)
