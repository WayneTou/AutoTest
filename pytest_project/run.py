# -*- coding: UTF-8 -*-
"""
@author: DouYueWei
@time: 2018/12/1 11:24
@usage:
"""
import os
import sys
import time

import yaml


class Run:
    def wirte_yml(self, download_address):
        path = os.path.abspath('config/node.yml')
        with open(path, 'r', encoding='utf-8') as f:
            res = yaml.load(f)
            f.close()
        with open(path, 'w', encoding='utf-8') as b:
            res['download_address'] = download_address
            yaml.dump(res, b)
            b.close()

    def run(self):
        now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        base_path = "cd C:/PlatON_autotest_workspace/base-code/pytest_project/testcase"
        excute_cases = " & pytest -v test_demo/test_web3_connection.py::test_request --html=../report/" + now + "PlatON_auto_test.html --junitxml=../report/" + now + "junit.xml"
        command = base_path + excute_cases
        os.system(command)

        with open('C:\\PlatON_autotest_workspace\\base-code\\pytest_project\\report\\' + now + 'PlatON_auto_test.html',
                  'r',
                  encoding='utf-8') as f:
            contain = f.read()
            f.close()
        with open(r'C:\Program Files (x86)\Jenkins\workspace\PlatON_auto_test\report\PlatON_auto_test.html', 'w',
                  encoding='utf-8') as b:
            b.write(contain)
            b.close()

        with open('C:\\PlatON_autotest_workspace\\base-code\\pytest_project\\report\\' + now + 'junit.xml', 'r',
                  encoding='utf-8') as junit_r:
            junit_contain = junit_r.read()
            junit_r.close()
        with open(r'C:\Program Files (x86)\Jenkins\workspace\PlatON_auto_test\report\junit.xml', 'w',
                  encoding='utf-8') as junit_w:
            junit_w.write(junit_contain)
            junit_w.close()


if __name__ == '__main__':
    r = Run()
    r.wirte_yml(sys.argv[1])
    r.run()
