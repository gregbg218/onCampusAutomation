import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.sender_email = "gasstation.usc@gmail.com"
        self.app_password = "YOUR_APP_PASSWORD_HERE"  # Replace with the App Password you generate
        self.receiver_email = "parkrsvp@usc.edu"

    def send_email(self, t2_data):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg['Subject'] = f"#{t2_data.get('R#')} - {t2_data.get('Event Name')}"

            body = f"""Parking Authorization for:

R#: {t2_data.get('R#')}
Event: {t2_data.get('Event Name')}
Date: {t2_data.get('Begin Date')} - {t2_data.get('End Date')}
Time: {t2_data.get('Begin Time')} - {t2_data.get('End Time')}
Location: {t2_data.get('Requested Lot')}
Department: {t2_data.get('Contact Department')}
Contact: {t2_data.get('Contact First Name')} {t2_data.get('Contact Last Name')}
Email: {t2_data.get('Contact E-mail')}
Phone: {t2_data.get('Contact Phone')}
Billing Code: {t2_data.get('billing_code')}"""

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.app_password)
            text = msg.as_string()
            
            print("[EMAIL] Sending email to parkrsvp@usc.edu...")
            server.sendmail(self.sender_email, self.receiver_email, text)
            print("[EMAIL] Email sent successfully")
            
            server.quit()
            return True

        except Exception as e:
            print(f"[ERROR] Failed to send email: {str(e)}")
            return False