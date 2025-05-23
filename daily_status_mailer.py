


import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_status_email(subject, body_text, sender_email, receiver_email,
                        smtp_server, smtp_port, smtp_username, smtp_password):
    """
    Sends an email with the given subject and body.

    Args:
        subject (str): The subject of the email.
        body_text (str): The plain text body of the email.
        sender_email (str): The email address of the sender.
        receiver_email (str or list): The email address(es) of the recipient(s).
                                      Can be a single string or a list of strings.
        smtp_server (str): The SMTP server hostname or IP address.
        smtp_port (int): The SMTP server port.
        smtp_username (str): The username for SMTP authentication.
        smtp_password (str): The password for SMTP authentication.

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

        # Connect to the SMTP server
        # Example for Gmail: smtp_server='smtp.gmail.com', smtp_port=587
        # Example for Outlook/Office365: smtp_server='smtp.office365.com', smtp_port=587
        # For other providers, check their SMTP settings.
        # Use smtplib.SMTP_SSL() for servers requiring SSL from the start (e.g., port 465)
        
        server = None # Initialize server to None for the finally block
        if smtp_port == 465: # SSL connection
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else: # TLS connection (typically port 587 or 25)
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()  # Extended Hello to server
            server.starttls()  # Secure the connection
            server.ehlo()  # Re-identify ourselves as an ESMTP client

        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipients_list, msg.as_string())
        
        logging.info(f"Email sent successfully to {', '.join(recipients_list)}.")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication Error: {e}. Check username/password. If using Gmail, consider 'App Passwords'.")
        return False
    except smtplib.SMTPServerDisconnected as e:
        logging.error(f"SMTP Server Disconnected: {e}. This might be due to TLS/SSL issues or server problems.")
        return False
    except smtplib.SMTPConnectError as e:
        logging.error(f"SMTP Connection Error: {e}. Check SMTP server address and port.")
        return False
    except smtplib.SMTPException as e: # Catch other SMTP related errors
        logging.error(f"SMTP Error: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except smtplib.SMTPServerDisconnected:
                logging.warning("Server was already disconnected.")
            except Exception as e_quit:
                logging.error(f"Error during server.quit(): {e_quit}")


def generate_status_report():
    # Example: Collect some data for the report
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



# Import the function if it's in daily_status_mailer.py
# from daily_status_mailer import send_status_email 

if __name__ == "__main__":
    # --- Configuration ---
    # !! IMPORTANT: Do NOT hardcode passwords in your script for production.
    # Use environment variables or a secure config management system.
    SMTP_SERVER = "smtp.audacy.com"  # Or your SMTP server
    SMTP_PORT = 587  # 587 for TLS, 465 for SSL
    SENDER_EMAIL = "jorge.rodriguez@@audacy.com"

    # For security, get credentials from environment variables
    SMTP_USERNAME = os.environ.get('MY_SMTP_USERNAME') # Or SENDER_EMAIL
    SMTP_PASSWORD = os.environ.get('MY_SMTP_PASSWORD')

    SMTP_USERNAME = 'Jorge.Rodriguez@@audacy.com'
    SMTP_PASSWORD = 'password' # Replace with your actual password or use environment variables
    
    RECEIVER_EMAIL = "recipient_email@example.com" # Can be a list: ["r1@example.com", "r2@example.com"]

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logging.error("SMTP username or password not found in environment variables.")
        # exit(1) # Or handle appropriately
    else:
        # --- Generate Report Content ---
        report_subject = "Daily Status Report - Project Alpha"
        report_body = generate_status_report() # Using the example function from above

        # --- Send the Email ---
        success = send_status_email(
            subject=report_subject,
            body_text=report_body,
            sender_email=SENDER_EMAIL,
            receiver_email=RECEIVER_EMAIL,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            smtp_username=SMTP_USERNAME,
            smtp_password=SMTP_PASSWORD
        )

        if success:
            logging.info("Status report email process completed successfully.")
        else:
            logging.error("Failed to send the status report email.")
