import smtplib
from email.mime.text import MIMEText

def send_alert(msg):

    sender = "manikandandhanush197@gmail.com"
    password = "zikf vqvl dztm andm"
    receiver = "dhanasekar112006@gmail.com"

    body = MIMEText(msg)
    body['Subject'] = "Laptop Risk Alert"
    body['From'] = sender
    body['To'] = receiver

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(body)
    server.quit()