from pytest_project.tools.send_email import send_email
from config.settings import BASE_DIR
import pytest
import os

if __name__ == '__main__':
    pytest.main(['-v', '-s', os.path.join(BASE_DIR, r'testcase/test_demo/test_demo.py'),
                '--html', os.path.join(BASE_DIR, r'report/autotest_report.html')])
    send_email(r'/home/runner/work/AutoTest/AutoTest/pytest_project/report/autotest_report.html')
