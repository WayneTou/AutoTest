# -*- coding: UTF-8 -*-
import os

from pytest_project.common import load_file
from pytest_project.platon_lib.platon_contract.platon_contract import PlatonContractTransaction


class TestTransaction:
    config_path = os.path.abspath('../config/node.yml')
    lf = load_file.LoadFile(config_path)
    config = lf.get_data()
    pt = PlatonContractTransaction(config['node1']['url'])
    address = str(pt.w3.toChecksumAddress(config['account1']['address']))
    password = str(config['account1']['password'])
    pt.w3.personal.unlockAccount(address, password, 99999999)
    pt2 = PlatonContractTransaction(config['node2']['url'])

    def new_account(self):
        recieve_address = self.pt.w3.toChecksumAddress(self.pt2.personal.newAccount('88888888'))
        return recieve_address

    def test_transaction(self):
        recieve_address = self.new_account()
        assert recieve_address is not None, '新增钱包地址异常，钱包地址为：{}'.format(recieve_address)
        before_balance = self.pt2.eth.getBalance(recieve_address)
        transaction = {'from': self.address, 'to': recieve_address, 'gas': '0xfffff',
                       'gasPrice': self.pt.eth.gasPrice, 'value': 1000000}
        trans_hash = self.pt.eth.sendTransaction(transaction)
        result = self.pt.eth.waitForTransactionReceipt(trans_hash)
        assert result is not None, '交易失败，交易结果为空'
        after_balance = self.pt2.eth.getBalance(recieve_address)
        assert (after_balance - before_balance) == 1000000, '转账ATP不正确，预期转账1000000，实际值：{}'.format(
            after_balance - before_balance)
