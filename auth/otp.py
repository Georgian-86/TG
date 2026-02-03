import random
import smtplib
from email.message import EmailMessage

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    msg = EmailMessage()
    msg.set_content(f"Your TeachGenie.ai OTP is: {otp}")
    msg["Subject"] = "TeachGenie.ai Login OTP"
    msg["From"] = "your_email@gmail.com"
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your_email@gmail.com", "APP_PASSWORD")
        server.send_message(msg)
