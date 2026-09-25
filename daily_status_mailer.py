import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.header import Header
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def send_status_email_gmail(subject, body_text, sender_email, receiver_email,
                             smtp_server, smtp_port, app_password):
    """
    Sends an email using Gmail App Password authentication.

    Args:
        subject (str): The subject of the email.
        body_text (str): The plain text body of the email.
        sender_email (str): The email address of the sender.
        receiver_email (str or list): The email address(es) of the recipient(s).
        smtp_server (str): The SMTP server hostname.
        smtp_port (int): The SMTP server port (typically 587 for Gmail).
        app_password (str): Gmail App Password (not regular password).

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        msg = MIMEText(body_text, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender_email

        if isinstance(receiver_email, list):
            recipients_list = receiver_email
            msg['To'] = ', '.join(recipients_list)
        else:
            recipients_list = [receiver_email]
            msg['To'] = receiver_email

        server = None
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        # Authenticate using App Password
        server.login(sender_email, app_password)
        
        server.sendmail(sender_email, recipients_list, msg.as_string())
        
        logging.info(f"Email sent successfully to {', '.join(recipients_list)}.")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication Error: {e}. Check your email and app password.")
        return False
    except smtplib.SMTPServerDisconnected as e:
        logging.error(f"SMTP Server Disconnected: {e}.")
        return False
    except smtplib.SMTPException as e:
        logging.error(f"SMTP Error: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except Exception as e_quit:
                logging.error(f"Error during server.quit(): {e_quit}")


def generate_status_report():
    tasks_completed = ["Task A", "Task B"]
    issues_found = ["Issue X"]
    system_status = "All systems operational."

    report_lines = [
        "Daily Status Report",
        "===================",
        f"System Status: {system_status}\n",
        "Tasks Completed Today:",
    ]
    for task in tasks_completed:
        report_lines.append(f"- {task}")

    report_lines.append("\nIssues/Blockers:")
    for issue in issues_found:
        report_lines.append(f"- {issue}")

    report_lines.append("\nHave a great day!")
    return "\n".join(report_lines)


<<<<<<< HEAD
# Import the function if it's in daily_status_mailer.py
# from daily_status_mailer import send_status_email 

if __name__ == "__main__":
    # --- Configuration ---
    # !! IMPORTANT: Do NOT hardcode passwords in your script for production.
    # Use environment variables or a secure config management system.
    SMTP_SERVER = "smtp.audacy.com"  # Or your SMTP server
    SMTP_PORT = int(os.environ.get('MY_SMTP_PORT', '587'))  # 587 for TLS, 465 for SSL
    SENDER_EMAIL = "jorge.rodriguez@audacy.com"

    # For security, get credentials from environment variables
    SMTP_USERNAME = os.environ.get('MY_SMTP_USERNAME', '')  # Or SENDER_EMAIL
    SMTP_PASSWORD = os.environ.get('MY_SMTP_PASSWORD', '')

    # Optional: use sender email as fallback username if desired
    # if not SMTP_USERNAME:
    #     SMTP_USERNAME = SENDER_EMAIL
    
    RECEIVER_EMAIL = "recipient_email@example.com" # Can be a list: ["r1@example.com", "r2@example.com"]

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logging.error("SMTP username or password not found in environment variables.")
        sys.exit(1)
    else:
        # --- Generate Report Content ---
=======
if __name__ == "__main__":
    # --- Gmail Configuration ---
    # To use Gmail:
    # 1. Enable 2-Factor Authentication on your Google Account
    # 2. Go to https://myaccount.google.com/apppasswords
    # 3. Generate an App Password for "Mail"
    # 4. Use that 16-character password (not your regular password)
    
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = os.environ.get('GMAIL_ADDRESS', 'your-email@gmail.com')
    GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', 'your-app-password-here')
    RECEIVER_EMAIL = "recipient_email@example.com"
    
    try:
        # Generate report
>>>>>>> 8c0abbe9e1f2f0f7eac93d41078f72929dc68476
        report_subject = "Daily Status Report - Project Alpha"
        report_body = generate_status_report()
        
        # Send email using Gmail
        success = send_status_email_gmail(
            subject=report_subject,
            body_text=report_body,
            sender_email=SENDER_EMAIL,
            receiver_email=RECEIVER_EMAIL,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            app_password=GMAIL_APP_PASSWORD
        )
        
        if success:
            logging.info("Status report email sent successfully.")
        else:
<<<<<<< HEAD
            logging.error("Failed to send the status report email.")
            logging.error("Failed to send the status report email.")
=======
            logging.error("Failed to send status report email.")
            
    except Exception as e:
        logging.error(f"Error in main execution: {e}")

>>>>>>> 8c0abbe9e1f2f0f7eac93d41078f72929dc68476
