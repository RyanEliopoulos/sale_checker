import smtplib
import os


class Notifier:

    @staticmethod
    def send_notification(message):
        login: str = os.getenv('ip_alert_email')
        password: str = os.getenv('ip_alert_email_pw')
        recipient_string: str = os.getenv('sale_checker_recipients')
        recipient_list = recipient_string.split(';')
        sm = smtplib.SMTP(host='smtp.gmail.com', port=587)
        sm.starttls()
        sm.login(login, password)
        for recipient in recipient_list:
            print(f'Notifying {recipient}: {message}')
            sm.sendmail(login, recipient, message)