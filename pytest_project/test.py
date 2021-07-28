import shutil
from tools.send_email import send_email
from config.settings import BASE_DIR
import os
import time

if __name__ == '__main__':
    cur_time = time.strftime(r'%Y-%m-%d %H:%M', time.localtime())

    db_folder = os.path.join(BASE_DIR, r'report')
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    zip_file_name = 'AutomationTestReport%s' % time.strftime(
        r'%Y%m%d%H%M')
    att_file_path = os.path.join(BASE_DIR, 'data', zip_file_name)
    shutil.make_archive(att_file_path, 'zip', db_folder)

    receive = ['wdou@deloitte.com.cn', 'dou_wayneyuewei@126.com']
    subject = 'Automation Test Execution %s' % cur_time
    with open(os.path.join(BASE_DIR, r'tools/email_demo.html'), 'r', encoding='utf-8') as file:
        content = file.read()
    file_path = att_file_path+'.zip'
    file_name = zip_file_name+'.zip'
    send_email(receive, subject, content, file_path=file_path,
               file_name=file_name)