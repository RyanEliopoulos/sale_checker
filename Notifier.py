import smtplib
import os


class Notifier:

    @staticmethod
    def send_notification(message):
        login: str = os.getenv('ip_alert_email')
        password: str = os.getenv('ip_alert_email_pw')
        recipient: str = os.getenv('sale_checker_recipient')
        sm = smtplib.SMTP(host='smtp.gmail.com', port=587)
        sm.starttls()
        sm.login(login, password)
        sm.sendmail(login, recipient, message)