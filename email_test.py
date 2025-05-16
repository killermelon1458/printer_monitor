# email_test.py
import os
from dotenv import load_dotenv
from pythonEmailNotify import EmailSender

# Load environment variables
load_dotenv(dotenv_path="/home/sovol/printer_monitor/printer_monitor.env")

# Setup email sender
emailer = EmailSender(
    smtp_server="smtp.gmail.com",
    port=587,
    login=os.environ["SMTP_EMAIL"],
    password=os.environ["SMTP_PASS"],
    default_recipient=os.environ["SMTP_TO"]
)

# Send test email
subject = "✅ SMTP Test from printer_monitor"
body = "This is a test to confirm that your SMTP login and .env configuration are working."

try:
    emailer.sendEmail(subject, body)
except Exception as e:
    print("❌ Failed to send test email.")
    import traceback
    traceback.print_exc()

