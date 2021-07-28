from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
import smtplib


def send_email(receive: list, subject, content, file_path, file_name):
    # 发送邮箱服务器
    smtpserver = "smtp.126.com"

    # 发送邮箱用户名密码
    user = "dou_wayneyuewei@126.com"
    password = "XXXXXX"

    # 发送和接收邮箱
    sender = "dou_wayneyuewei@126.com"
    receive = receive
    # ['dou_wayneyuewei@126.com']

    # 发送邮件主题和内容
    subject = subject
    content = content

    # HTML邮件正文
    send_file = open(file_path, "rb").read()

    # 添加附件
    att = MIMEText(send_file, "base64", 'utf-8')
    att['Content-Type'] = 'application/octet-stream'
    att['Content-Disposition'] = 'attachment;filename="%s"' % file_name

    msg = MIMEMultipart()
    msg.attach(MIMEText(content, 'html', 'utf-8'))
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ";".join(receive)
    msg.attach(att)

    # SSL协议端口号要使用465
    smtp = smtplib.SMTP_SSL(smtpserver, 465)

    # HELO向服务器标志用户身份
    smtp.helo(smtpserver)

    # 服务器返回结果确认
    smtp.ehlo(smtpserver)

    # 登录邮箱服务器用户名密码
    smtp.login(user, password)

    print("Send email start...")
    smtp.sendmail(sender, receive, msg.as_string())
    smtp.quit()
    print("email send end!")
