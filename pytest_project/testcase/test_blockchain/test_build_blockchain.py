import time
import operator
from pytest_project.common.connect import connect_web3
from pytest_project.common.auto_deploy_platon import AutoDeployPlaton


class TestBuildBlockChain:
    auto = AutoDeployPlaton()
    rpc_url, bootnodes_list = auto.start_multi_node('../config/node.yml')
    one_node_yml = '../config/one_node.yml'
    w3_list = [connect_web3(url) for url in rpc_url]

    def test_blocknumber(self):
        '''
        测试块高是否正常增长
        '''
        for w3 in self.w3_list:
            start_block = w3.eth.blockNumber
            time.sleep(20)
            end_block = w3.eth.blockNumber
            assert 15 <= (end_block-start_block) <= 25, '区块增长不在允许的范围内'

    def test_blockinfo(self):
        '''
        测试所有节点区块信息是否一致
        '''
        w3 = self.w3_list[0]
        blocknumber = w3.eth.blockNumber
        blockinfo = w3.eth.getBlock(blocknumber)
        for w in self.w3_list[1:-1]:
            info = w3.eth.getBlock(blocknumber)
            assert blockinfo == info, "不同节点的相同块高信息不一致"

    def check_join(self, rpc_url, net_num_1, message="公链"):
        '''
        用于相同的genesis.json加入节点后的校验
        '''
        w3 = connect_web3(rpc_url)
        # 先判断公链节点数是否正常增加
        net_num_2 = self.w3_list[0].net.peerCount
        assert net_num_2 > net_num_1, "{}节点数没有增加".format(message)
        # 判断是否加入到对应的公链
        peers = w3.admin.peers
        assert peers is not None, "加入{}失败，peers为空".format(message)
        p_id = []
        for peer in peers:
            p_id(peer.get('id'))
        assert operator.eq(
            self.p2p_id, p_id), "加入链的节点id与{}的id不一致".format(message)

    def test_join_add(self):
        '''
        测试相同的genesis.json节点加入addPeer
        '''
        # 不初始化调用搭建节点的方法，得到一个rpc_url
        rpc_url, _ = self.auto.start_one_node(self.one_node_yml)
        net_num_1 = self.w3_list[0].net.peerCount
        w3 = connect_web3(rpc_url)
        w3.admin.addPeer(self.bootnodes_list[0])
        self.check_join(rpc_url, net_num_1)

    def test_join_bootnodes(self):
        '''
        测试相同的genesis.json节点加入--bootnodes
        '''
        net_num_1 = self.w3_list[0].net.peerCount
        # 不初始化调用搭建节点的方法，得到一个rpc_url,需要配置公链的--bootnodes
        rpc_url, _ = self.auto.start_one_node(
            self.one_node_yml, bootnodes_id=self.bootnodes_list[0])
        self.check_join(rpc_url, net_num_1)

    def check_join_diff(self, rpc_url, net_num_1, message="公链"):
        '''
        用于使用不同的genesis.json加入节点后的校验
        '''
        w3 = connect_web3(rpc_url)
        # 先判断公链节点数是否正常增加
        net_num_2 = self.w3_list[0].net.peerCount
        assert net_num_2 == net_num_1, "{}节点数有增加".format(message)
        # 判断是否加入到对应的公链
        peers = w3.admin.peers
        assert len(peers) is 0, "peers节点数不为空"

    def test_join_add_diff(self):
        '''
        使用不同genesis.json，addPeer
        '''
        # 初始化调用搭建节点的方法，得到一个rpc_url
        rpc_url, _ = self.auto.start_one_node(
            self.one_node_yml, is_need_init=False)
        net_num_1 = self.w3_list[0].net.peerCount
        w3 = connect_web3(rpc_url)
        w3.admin.addPeer(self.bootnodes_list[0])
        self.check_join_diff(rpc_url, net_num_1)

    def test_join_bootnodes_diff(self):
        '''
        使用不同genesis.json，--bootnodes
        '''
        net_num_1 = self.w3_list[0].net.peerCount
        # 不初始化调用搭建节点的方法，得到一个rpc_url,需要配置公链的--bootnodes
        rpc_url, _ = self.auto.start_one_node(
            self.one_node_yml, is_need_init=False, bootnodes_id=self.bootnodes_list[0])
        self.check_join_diff(rpc_url, net_num_1)

    def test_not_join(self):
        '''
        不初始化，也不加入公链启动
        '''
        # 部署一个节点，启动，得到对应的rpc_url
        rpc_url, _ = self.auto.start_one_node(
            self.one_node_yml, is_need_init=False)
        w3 = connect_web3(rpc_url)
        start_block = w3.eth.blockNumber
        time.sleep(3)
        end_block = w3.eth.blockNumber
        assert start_block == end_block, "区块高度不一致"

    def test_build_privatechain(self):
        '''
        部署单节点私链
        '''
        # 部署一个单节点私链，genesis.json中，nodeid只有一个，启动后配置该nodeid对应的nodekey，得到对应的rpc_url
        rpc_url, _ = self.auto.start_one_node(self.one_node_yml)
        w3 = connect_web3(rpc_url)
        start_block = w3.eth.blockNumber
        time.sleep(3)
        end_block = w3.eth.blockNumber
        assert start_block <= end_block, "区块高度没有增长"
