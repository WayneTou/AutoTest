# -*- coding: UTF-8 -*-
"""
@author: DouYueWei
@time: 2019/1/3 16:27
@usage:
"""
import time
import logging
import traceback

from apscheduler.schedulers.blocking import BlockingScheduler
from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware

# 监控节点list
url_list = ['http://10.10.8.234:6789', 'http://10.10.8.235:6789', 'http://10.10.8.236:6789', 'http://10.10.8.237:6789',
            'http://10.10.8.239:6789',]

# url_list = ['http://10.10.8.234:6789', 'http://10.10.8.235:6789', 'http://10.10.8.236:6789', 'http://10.10.8.237:6789',
#             'http://10.10.8.239:6789', 'http://192.168.112.120:6789', 'http://192.168.112.121:6789', 'http://192.168.112.122:6789',
#             'http://192.168.112.123:6789', 'http://192.168.112.124:6789']

sched = BlockingScheduler()


class Logger:
    def __init__(self, name, log_file_name):
        fmt = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=fmt)
        self.logger = logging.getLogger(name)
        handler = logging.FileHandler(log_file_name, encoding='utf-8')
        handler.setLevel(level=logging.INFO)
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


def list_establish(L: list):
    w3_list = [Web3(HTTPProvider(url)) for url in url_list]
    for w3 in w3_list:
        w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    for w3 in w3_list:
        num = w3.eth.blockNumber
        L.append(num)
    del w3_list


@sched.scheduled_job('interval', seconds=60)
def monitoring_blockNumber():
    lg = Logger('block_monitor', 'block_monitor_log2.out')
    L = []
    L2 = []
    list_establish(L2)
    time.sleep(5)
    for i in range(10):
        list_establish(L)
        lg.logger.info('块高list:{}'.format(L))
        if max(L) - min(L) > 5:
            high = L.index(max(L))
            low = L.index(min(L))
            data = "块高差异过大，最高节点：{}，最低节点：{},差值：{}".format(url_list[high], url_list[low], max(L) - min(L))
            lg.logger.error(data)
        for i in range(len(L)):
            if L[i] == L2[i]:
                lg.logger.error('{} 节点，过去5秒块高未增长,当前块高：{}'.format(url_list[i], L[i]))
        L2 = L.copy()
        L.clear()
        time.sleep(5)


@sched.scheduled_job('interval', seconds=60)
def monitoring_timestamp():
    lg = Logger('timestamp_monitor', 'timestamp_monitor_log2.out')
    for i in range(11):
        w3 = Web3(HTTPProvider(url_list[0]))
        w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        num = w3.eth.blockNumber
        time_diff = w3.eth.getBlock(num)['timestamp'] - w3.eth.getBlock(num - 1)['timestamp']
        if time_diff <= 0 or time_diff > 2000:
            data = "区块间隔时间差值过大，相邻区块{},{}，时间差：{}毫秒".format(num - 1, num, time_diff)
            lg.logger.error(data)
        del w3
        time.sleep(5)


if __name__ == "__main__":
    try:
        sched.start()
    except Exception as e:
        traceback.extract_stack()
        print(e)
