#알림을 전송하는 기능을 담당합니다 (이메일, Slack, Google Chat 등).

import smtplib
from email.mime.text import MIMEText

from pyexpat.errors import messages

from config import EMAIL_ID, EMAIL_PW

def write_email(subject, body):
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = EMAIL_ID
    #message['To'] = "minu8165@gmail.com"              #To_email은 mailing_list를 보고 결정하기
    message['Subject'] = subject+'에 관한 메일(Telegram_Alert_Service'

    return message


def send_email(subject, body):
    try:

        to_email="minu8165@gmail.com"
        message = write_email(subject, body)

        mail_server = smtplib.SMTP("smtp.gmail.com", 587)
        mail_server.starttls()  # Gmail 등 대부분의 서비스는 TLS 사용 (암호화)
        mail_server.login(EMAIL_ID, EMAIL_PW)
        # text = msg.as_string()  # 이메일 본문을 문자열로 변환

        mail_server.sendmail(EMAIL_ID, to_email, message.as_string()) #to email.
        mail_server.quit()

        print(f"이메일 전송을 완료했습니다.")

    except Exception as e:
        print("Error : ", e)
#     msg = MIMEMultipart()
#     msg["From"] = FROM_EMAIL
#
# sender_email = "kminu616@gmail.com"


#slack를 추가하기
