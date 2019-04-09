# -*- coding: UTF-8 -*-
import os

from pytest_project.common import load_file
from pytest_project.platon_lib.platon_contract import platon_contract
from pytest_project.platon_lib.platon_contract.platon_contract import PlatonContractTransaction


class TestContract:
    config_path = os.path.abspath('../config/node.yml')
    lf = load_file.LoadFile(config_path)
    config = lf.get_data()
    pt = PlatonContractTransaction(config['node1']['url'])
    address = pt.w3.toChecksumAddress(config['account1']['address'])
    password = config['account1']['password']
    pt.w3.personal.unlockAccount(str(address), str(password), 99999999)

    def test_contract_deploy(self):
        wasm_path = os.path.abspath('../casedata/contract/inputtest.wasm')
        abi_path = os.path.abspath('../casedata/contract/inputtest.cpp.abi.json')
        deploy_trans_hash = self.pt.contract_deploy(1,
                                                    platon_contract.get_byte_code(wasm_path),
                                                    platon_contract.get_abi_bytes(abi_path),
                                                    self.address)
        result = self.pt.eth.waitForTransactionReceipt(deploy_trans_hash)
        contract_address = result['contractAddress']
        print(contract_address)
        assert contract_address is not None, '合约部署失败，合约地址为空'
        contract_code = self.pt.eth.getCode(contract_address)
        assert len(contract_code) > 3, '合约部署异常，getCode(contract_address)结果异常'
