from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
import smtplib

def send_email(file_path=r'C:\Workspace\AutoTest\pytest_project\report\autotest_report.html'):
    # 发送邮箱服务器
    smtpserver = "smtp.126.com"

    # 发送邮箱用户名密码
    user = "dyw2009@126.com"
    password = "BAMRLDLKMZKBHFNM"

    # 发送和接收邮箱
    sender = "dyw2009@126.com"
    receive = "wdou@deloitte.com.cn"

    # 发送邮件主题和内容
    subject = "Web Selenium 自动化测试报告"
    content = "<html><h1 style='color:red'>自动化测试，自学成才</h1></html>"

    # HTML邮件正文
    send_file = open(file_path, "rb").read()

    att = MIMEText(send_file, "base64", 'utf-8')
    att['Content-Type'] = 'application/octet-stream'
    att['Content-Disposition'] = 'attachment;filename="autotest_report.html"'

    msg = MIMEMultipart()
    msg.attach(MIMEText(content, 'html', 'utf-8'))
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receive
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