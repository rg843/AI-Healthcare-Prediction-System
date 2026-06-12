import os
import logging
from typing import Optional

logger = logging.getLogger('healthcare.sms')
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)

TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_FROM')


def send_sms(number: str, message: str):
    # If Twilio env vars present, attempt to send via Twilio REST API
    if TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and number:
        try:
            from twilio.rest import Client
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            msg = client.messages.create(body=message, from_=TWILIO_FROM, to=number)
            logger.info('SMS sent to %s sid=%s', number, getattr(msg, 'sid', None))
            return True
        except Exception:
            logger.exception('Twilio send failed')
            return False
    # fallback: log the message if number provided
    if number:
        logger.info('DRY-RUN SMS to=%s message="%s"', number, message)
        return True
    logger.warning('No SMS provider configured and no number provided')
    return False
