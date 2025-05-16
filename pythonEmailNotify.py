import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

class EmailSender:
    def __init__(self, smtp_server, port, login, password, default_recipient=None):
        """
        Initialize the email sender with SMTP details.
        :param smtp_server: SMTP server address (e.g., "smtp.gmail.com").
        :param port: SMTP server port (e.g., 587 for TLS).
        :param login: Login email for the SMTP server.
        :param password: Password or app password for the SMTP server.
        :param default_recipient: Optional default recipient email address.
        """
        self.smtp_server = smtp_server
        self.port = port
        self.login = login
        self.password = password
        self.default_recipient = default_recipient

    def sendEmail(self, subject, body, recipient=None, html=False):
        """
        Send an email with the specified subject and body.
        :param subject: Subject of the email.
        :param body: Body of the email (plain text or HTML).
        :param recipient: Recipient email address. Uses default_recipient if None.
        :param html: Set to True if body is HTML content.
        """
        if recipient is None and self.default_recipient is None:
            raise ValueError("Recipient email must be specified.")

        recipient = recipient or self.default_recipient

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = self.login
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html' if html else 'plain'))

        try:
            # Send email
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.login, self.password)
                server.send_message(msg)
            print(f"Email sent successfully to {recipient}.")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def sendException(self, exception, recipient=None):
        """
        Send an email with exception details.
        :param exception: The exception object.
        :param recipient: Recipient email address. Uses default_recipient if None.
        """
        subject = "Exception Occurred in Script"
        body = f"""
        <h1>Exception Report</h1>
        <p><strong>Type:</strong> {type(exception).__name__}</p>
        <p><strong>Message:</strong> {exception}</p>
        <p><strong>Traceback:</strong></p>
        <pre>{traceback.format_exc()}</pre>
        """
        self.sendEmail(subject, body, recipient, html=True)

