from flask_mail import Message
from . import mail

def send_email(recipient_mail, otp, body):
  msg = Message(f'Here is your OTP for verification : {otp}', recipients=[recipient_mail])
  msg.body = (body)
  msg.html = (f'<h1>{body}</h1>'
              f'<p>Here is your OTP for verification : {otp}</p>')
  mail.send(msg)
