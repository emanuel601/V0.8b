import os
import smtplib


# This class is responsible for sending notifications.


class NotificationManager:
    def __init__(self):
        self.email_account = os.getenv('YOUR_EMAIL_MANAGER_ACCOUNT')
        self.email_account_administrator = os.getenv('EMAIL_ADMINISTRATOR_ACCOUNT')

    def send_email(self, name, email, subject, message):

        my_email = self.email_account
        administrator_email = self.email_account_administrator
        password = os.getenv("KEY_EMAIL")
        with smtplib.SMTP("smtp.office365.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email, to_addrs=administrator_email,
                                msg=f"Subject:{subject} \n\n Email: {email} \n Nombre: {name} \n Mensaje: {message}")
