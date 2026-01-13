"""
Email Sender Module with Gmail Integration
Supports both SMTP and Gmail API for sending reports
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    """Handles sending emails via SMTP"""
    
    def __init__(self, smtp_server: str, smtp_port: int, email_address: str, email_password: str):
        """
        Initialize email sender
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            email_address: Sender email address
            email_password: Email password or app-specific password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.email_password = email_password
    
    def send_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        body_text: str = None,
        body_html: str = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_emails: Recipient email address(es)
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = self.email_address
            
            # Handle single or multiple recipients
            if isinstance(to_emails, str):
                recipients_list = [to_emails]
                msg['To'] = to_emails
            else:
                recipients_list = to_emails
                msg['To'] = ', '.join(recipients_list)
            
            # Attach body parts
            if body_text:
                part_text = MIMEText(body_text, 'plain', 'utf-8')
                msg.attach(part_text)
            
            if body_html:
                part_html = MIMEText(body_html, 'html', 'utf-8')
                msg.attach(part_html)
            
            # Connect and send
            server = None
            try:
                if self.smtp_port == 465:  # SSL connection
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                else:  # TLS connection (typically port 587)
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, recipients_list, msg.as_string())
                
                logger.info(f"Email sent successfully to {', '.join(recipients_list)}")
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP Authentication Error: {e}")
                logger.error("Check username/password. For Gmail, use 'App Passwords'.")
                return False
            except smtplib.SMTPServerDisconnected as e:
                logger.error(f"SMTP Server Disconnected: {e}")
                return False
            except smtplib.SMTPConnectError as e:
                logger.error(f"SMTP Connection Error: {e}")
                return False
            except smtplib.SMTPException as e:
                logger.error(f"SMTP Error: {e}")
                return False
            finally:
                if server:
                    try:
                        server.quit()
                    except (smtplib.SMTPServerDisconnected, Exception) as e_quit:
                        logger.warning(f"Error during server.quit(): {e_quit}")
                        
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False
    
    def send_report(
        self,
        to_emails: Union[str, List[str]],
        report_title: str,
        report_text: str,
        report_html: str = None
    ) -> bool:
        """
        Send a report via email
        
        Args:
            to_emails: Recipient email address(es)
            report_title: Title of the report
            report_text: Plain text version of report
            report_html: HTML version of report (optional)
            
        Returns:
            True if sent successfully
        """
        subject = f"Jira Daily Report - {report_title}"
        return self.send_email(to_emails, subject, report_text, report_html)


class GmailSender(EmailSender):
    """
    Gmail-specific email sender
    Extends EmailSender with Gmail defaults
    """
    
    def __init__(self, email_address: str, app_password: str):
        """
        Initialize Gmail sender
        
        Args:
            email_address: Gmail address
            app_password: Gmail app-specific password
                         (Generate at: https://myaccount.google.com/apppasswords)
        """
        super().__init__(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            email_address=email_address,
            email_password=app_password
        )
        logger.info("Gmail sender initialized. Remember to use App Passwords!")


def create_email_sender(config: dict) -> EmailSender:
    """
    Factory function to create appropriate email sender
    
    Args:
        config: Email configuration dictionary with keys:
               - address: email address
               - password: email password/app password
               - smtp_server: SMTP server (optional, defaults to Gmail)
               - smtp_port: SMTP port (optional)
    
    Returns:
        EmailSender instance
    """
    email_address = config.get('address')
    password = config.get('password')
    smtp_server = config.get('smtp_server', 'smtp.gmail.com')
    smtp_port = config.get('smtp_port', 587)
    
    if not email_address or not password:
        raise ValueError("Email address and password are required")
    
    # Use Gmail sender for Gmail addresses
    if 'gmail.com' in email_address.lower() and smtp_server == 'smtp.gmail.com':
        return GmailSender(email_address, password)
    
    return EmailSender(smtp_server, smtp_port, email_address, password)
