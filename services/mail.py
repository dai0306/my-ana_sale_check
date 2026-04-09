import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

from config import settings

logger = logging.getLogger(__name__)

def send_email_with_retry(subject, body, retries=3, base_delay=2):
  msg = MIMEText(body, "plain", "utf-8")
  msg["Subject"] = subject
  msg["From"] = settings.FROM_EMAIL
  msg["To"] = settings.TO_EMAIL
  msg["Date"] = formatdate(localtime=True)

  for count in range(retries):
   
   try:
    with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.PORT) as server:
      server.login(settings.FROM_EMAIL, settings.APP_PASSWORD)
      server.set_debuglevel(0)
      server.send_message(msg)
      logger.info("メール送信")
    return True
    
   except smtplib.SMTPRecipientsRefused as e:
     logger.error("宛先拒否:%s", e)
     return False
   
   except Exception as e:
     logger.warning("送信失敗(%d/%d) : %s", count+1, retries, e, exc_info=True)
     time.sleep(base_delay* (2**count))
     return False