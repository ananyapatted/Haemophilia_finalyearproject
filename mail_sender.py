import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket

def is_smtp_server_up(server, port, timeout=10):
    """Check if the SMTP server is up by attempting a socket connection."""
    try:
        server_address = (server, port)
        sock = socket.create_connection(server_address, timeout=timeout)
        sock.close()
        return True
    except socket.error as e:
        print(f"Failed to connect to server. Error: {e}")
        return False

def send_email(subject, message, to_email, from_email='hemophilla.project@outlook.com', password='hemophilla123', timeout=30):
    # Outlook SMTP server settings
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587 
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the message to the MIMEMultipart object
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Create server object with TLS option
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)
        server.starttls()  # Start TLS encryption
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"Successfully sent email to {to_email}")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
        raise

def send_registration_email(user_email, username, password):
    subject = "Welcome to Hemophilla Project!"
    message = f"""
    Dear User,

    Welcome to Hemophilla Project! You have been successfully registered.

    Your login details are as follows:
    - Username: {username}
    - Password: {password}

    For your security, we strongly recommend that you log in and reset your password immediately. You can do this by visiting the profile or settings page after you log in.

    If you have any questions or need assistance, please do not hesitate to contact our support team.

    Thank you for joining Hemophilla Project!

    Best regards,
    The Hemophilla Project Team
    """
    try:
        send_email(subject, message, user_email)
    except Exception as e:
        print("Failed to send email. Error: %s" % str(e))
        raise
