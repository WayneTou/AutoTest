# -*- coding: UTF-8 -*-
import requests

from pytest_project.platon_lib.platon_contract.platon_contract import PlatonContractTransaction


def test_request():
    print('test request')
    resp = requests.get('https://www.baidu.com')
    assert resp.status_code == 200


def test_web3():
    wt = PlatonContractTransaction("http://192.168.9.175:6789")
    print("2")
    assert wt.w3 is not None
