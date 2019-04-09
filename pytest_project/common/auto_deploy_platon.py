import os
import json
import time

from pytest_project.common.connect import connect_linux
from pytest_project.common.load_file import LoadFile
import re


def file_exists(*args):
    for i in args:
        if not os.path.exists(os.path.abspath(i)):
            raise Exception("文件{}不存在".format(i))


def re_result(msg, pattern):
    msg = re.sub("(\r)", "", msg)
    msg = re.sub("(\n)", "", msg)
    msg = re.sub(" ", "", msg)
    result = re.findall(pattern, msg)
    return result


class AutoDeployPlaton:
    def __init__(
            self, platon='../casedata/platon/platon',
            cbft='../casedata/platon/cbft.json',
            keystore='../casedata/keystore/UTC--2018-10-04T09-02-39.439063439Z--493301712671ada506ba6ca7891f436d29185821',
            genesis='../casedata/platon/genesis.json',
            go=None
    ):
        '''
        platon节点部署
        params:
            @platon:platon文件的相对路径或绝对路径
            @cbft:cbft文件的相对路径或绝对路径
            @keytore:keytore文件的相对路径或绝对路径
            @genesis:genesis文件的相对路径或绝对路径
            @go:go文件的相对路径或绝对路径,用户部署节点机器的go环境搭建，暂不支持
        '''
        if go:
            file_exists(platon, cbft, keystore, genesis, go)
            self.go = os.path.abspath(go)
        else:
            file_exists(platon, cbft, keystore, genesis)
            self.go = go
        self.platon = os.path.abspath(platon)
        self.cbft = os.path.abspath(cbft)
        self.keystore = os.path.abspath(keystore)
        self.genesis = os.path.abspath(genesis)
        # start_once 用于计算启动失败后重新启动的尝试次数
        self.start_once = 0

    def start_platon(self, ssh, cmd=None, bootnodes_id=None):
        '''启动platon进程'''
        if not cmd:
            cmd = '''nohup ./platon/platon --identity "platon" --rpc --datadir ./platon/data --port 16789 --rpcport 6789 --rpcapi "db,eth,net,web3,miner,admin,personal" --rpcaddr 0.0.0.0 --nodiscover > ./platon/nohup.out 2>&1 &'''
        if bootnodes_id:
            # 以加入其他节点的方式启动
            cmd = '''nohup ./platon/platon --identity "platon" --rpc --datadir ./platon/data --port 16789 --rpcport 6789 --rpcapi "db,eth,net,web3,miner,admin,personal" --rpcaddr 0.0.0.0 --bootnodes="{}" --nodiscover > ./platon/nohup.out 2>&1 &'''.format(
                bootnodes_id)
        ssh.exec_command(cmd)
        # 延时避免启动失败
        time.sleep(3)
        _, out, _ = ssh.exec_command('ps -ef|grep platon')
        out_list = out.readlines()
        if not out_list:
            # 返回输出为空说明启动失败
            return
        for p in out_list:
            # 查询进程是否存在，有则说明启动成功，暂时没有更好的方法
            if re_result(p, 'db,eth,net,web3,miner,admin,personal'):
                return True
        return

    def remove_platon(self, ssh, cmd=None):
        '''删除'''
        if not cmd:
            cmd = 'rm -rf ./platon'
        ssh.exec_command(cmd)
        time.sleep(1)

    def init_platon(self, ssh, cmd=None):
        '''初始化'''
        if not cmd:
            cmd = './platon/platon --datadir ./platon/data init ./platon/genesis.json'
        ssh.exec_command(cmd)
        time.sleep(2)

    def stop_platon(self, ssh, value=None):
        '''关闭platon进程'''
        if not value:
            value = 'db,eth,net,web3,miner,admin,personal'
        _, out, _ = ssh.exec_command('ps -ef|grep platon')
        out_list = out.readlines()
        if not out_list:
            # 返回为空说明不存在platon进程
            return
        for p in out_list:
            if re_result(p, value):
                # 获取platon进程id并关闭
                p_id = [i for i in p.split(" ") if i][1]
                ssh.exec_command('kill -9 {}'.format(p_id))
                time.sleep(0.5)

    def kill_platon(self, nodedicts):
        '''
        @Description: 启动前先关闭所有的platon进程
        @param {type} @@@@
        @return: @@@@
        '''
        for k in nodedicts.keys():
            if 'node' in k:
                ip = nodedicts[k].get('host')
                username = nodedicts[k].get('username')
                password = nodedicts[k].get('password')
                ssh, _, t = connect_linux(ip, username, password)
                self.stop_platon(ssh)
                self.stop_platon(ssh, '16789')
                self.stop_platon(ssh, '6789')
                t.close()

    def get_static_and_genesis(self, nodedicts):
        '''
        nodedicts:
            @
            {
                'node1': 
                    {
                        'host': '192.168.9.175', 
                        'url': 'http://192.168.9.175:6789', 
                        'id': '97e424be5e58bfd4533303f8f515211599fd4ffe208646f7bfdf27885e50b6dd85d957587180988e76ae77b4b6563820a27b16885419e5ba6f575f19f6cb36b0', 
                        'nodekey': '87787aeee9540ec942629b5cbf3bbcc4c765ec02129943ef7463d2864f188938',
                        'username': 'root', 
                        'password': 'Juzhen123!'
                    }, 
                'node2': 
                    {
                        'host': 
                        '192.168.9.176', 
                        'url': 'http://192.168.9.176:6789', 
                        'id': '3b53564afbc3aef1f6e0678171811f65a7caa27a927ddd036a46f817d075ef0a5198cd7f480829b53fe62bdb063bc6a17f800d2eebf7481b091225aabac2428d', 
                        'nodekey': 'aa4aac7a35a7bdf60b69b8aa19b941c04bdae48b305933ed07117291b682ca6b'
                        'username': 'root', 
                        'password': 'Juzhen123!'
                    }
            }
        return:
            @static_nodes:用于创建static-nodes.json文件
            @genesis_id_list:用于创建genesis.json文件
        '''
        static_nodes = []
        genesis_id_list = []
        for k in nodedicts.keys():
            if "node" in k:
                public_value = r"enode://" + \
                               nodedicts[k].get("id") + "@" + \
                               nodedicts[k].get("host") + ":16789"
                static_nodes.append(public_value)
                genesis_id_list.append(nodedicts[k].get("id"))
        return static_nodes, genesis_id_list

    def start_multi_node(self, config_yaml, genesis_file=None, static_node_file=None, is_need_init=True,
                         bootnodes_id=None):
        '''
        多节点启动
        params:
            @config_yaml:节点配置文件
            @genesis_file:初始化需要的文件，默认根据config_yaml文件生成
            @static_node_file:节点互连配置文件，默认config_yaml文件生成
            @is_need_init:是否需要初始化genesis.json,默认是
            @boootnodes_id:节点连接公钥,用于启动时自动连接其他节点，"enode://288b97262895b1c7ec61cf314c2e2004407d0a5dc77566877aad1f2a36659c8b698f4b56fd06c4a0c0bf007b4cfb3e7122d907da3b005fa90e724441902eb19e@XXX:30303"
        return:
            @rpc_url_list:节点rpc连接url列表
            @bootnodes_id_list:节点公钥id列表
        '''
        node_yaml = os.path.abspath(config_yaml)
        # 获取yaml文件信息
        nodedicts = LoadFile(node_yaml).get_data()
        static_nodes, genesis_id_list = self.get_static_and_genesis(nodedicts)
        if not static_node_file:
            # 如果有传入static_node_file，则不需要新建static-nodes.json
            static_node_file = os.path.abspath(
                '../casedata/platon/static-nodes.json')
            num = 0
            with open(static_node_file, 'w', encoding='utf-8')as f:
                f.write('[\n')
                for i in static_nodes:
                    num += 1
                    if num < len(static_nodes):
                        f.write('\"' + i + '\",\n')
                    else:
                        f.write('\"' + i + '\"\n')
                f.write(']')
        rpc_url_list = []
        bootnodes_id_list = []
        if is_need_init:
            if not genesis_file:
                genesis_file = os.path.abspath('../casedata/genesis.json')
                genesis_data = LoadFile(self.genesis).get_data()
                genesis_data['config']['cbft']["initialNodes"] = genesis_id_list
                with open(genesis_file, 'w', encoding='utf-8')as f:
                    f.write(json.dumps(genesis_data))
        self.kill_platon(nodedicts)
        for k in nodedicts.keys():
            if 'node' in k:
                self.start_once = 0
                rpc_url, bootnodes_id = self.start_node(
                    nodedict=nodedicts[k], genesis_file=genesis_file, static_node_file=static_node_file,
                    bootnodes_id=None
                )
                rpc_url_list.append(rpc_url)
                bootnodes_id_list.append(bootnodes_id)
        return rpc_url_list, bootnodes_id_list

    def start_one_node(self, config_yaml, genesis_file=None, static_node_file=None, is_need_init=True,
                       bootnodes_id=None):
        '''
        单节点启动
        params:
            @config_yaml:节点配置文件
            @genesis_file:初始化需要的文件，默认根据config_yaml文件生成
            @static_node_file:节点互连配置文件，默认config_yaml文件生成
            @is_need_init:是否需要初始化genesis.json,默认是
            @boootnodes_id:节点连接公钥,用于启动时自动连接其他节点，"enode://288b97262895b1c7ec61cf314c2e2004407d0a5dc77566877aad1f2a36659c8b698f4b56fd06c4a0c0bf007b4cfb3e7122d907da3b005fa90e724441902eb19e@XXX:30303"
        return:
            @rpc_url:节点rpc连接url
            @bootnodes_id:节点公钥id
        '''
        node_yaml = os.path.abspath(config_yaml)
        nodedict = LoadFile(node_yaml).get_data()
        if is_need_init:
            if not genesis_file:
                genesis_id_list = []
                genesis_id_list.append(nodedict.get('id'))
                genesis_file = os.path.abspath('../casedata/genesis.json')
                genesis_data = LoadFile(self.genesis).get_data()
                genesis_data['config']['cbft']["initialNodes"] = genesis_id_list
                with open(genesis_file, 'w', encoding='utf-8')as f:
                    f.write(json.dumps(genesis_data))
        rpc_url, bootnodes_id = self.start_node(
            nodedict=nodedict, genesis_file=genesis_file, static_node_file=static_node_file,
            bootnodes_id=bootnodes_id
        )
        return rpc_url, bootnodes_id

    def restart_multi_node(self, config_yaml):
        '''重启多节点,主要用于性能测试中,需要保留环境中的部分数据'''
        node_yaml = os.path.abspath(config_yaml)
        nodedicts = LoadFile(node_yaml).get_data()
        self.kill_platon(nodedicts)
        for k in nodedicts.keys():
            if 'node' in k:
                self.start_once = 0
                rpc_url, bootnodes_id = self.restart_node(
                    nodedicts[k])

    def restart_node(self, nodedict):
        '''重启节点,主要用于性能测试中,需要保留环境中的部分数据'''
        try:
            ip = nodedict["host"]
        except KeyError as e:
            raise e
        username = nodedict.get("username")
        password = nodedict.get("password")
        if username and password:
            ssh, sftp, t = connect_linux(ip, username, password)
        else:
            ssh, sftp, t = connect_linux(ip)
        self.remove_platon(ssh, 'rm -rf ./platon/data/platon')
        sftp.put(self.platon, './platon/platon')
        ssh.exec_command('chmod +x ./platon/platon')
        time.sleep(0.05)
        ssh.exec_command('> ./platon/nohup.out')
        start_result = self.start_platon(ssh)
        if not start_result:
            self.stop_platon(ssh)
            if self.start_once > 3:
                raise Exception("节点{}无法启动".format(nodedict.get("url")))
            self.start_once += 1
            return self.restart_node(nodedict)
        t.close()
        rpc_url = nodedict.get("url")
        bootnodes_id = r"enode://" + \
                       nodedict.get("id") + "@" + \
                       nodedict.get("host") + ":16789"
        return rpc_url, bootnodes_id

    def start_node(self, nodedict, genesis_file, static_node_file, bootnodes_id):
        '''
        nodedict:
            @
            {
                'host': '192.168.9.175', 
                'url': 'http://192.168.9.175:6789', 
                'id': '97e424be5e58bfd4533303f8f515211599fd4ffe208646f7bfdf27885e50b6dd85d957587180988e76ae77b4b6563820a27b16885419e5ba6f575f19f6cb36b0', 
                'nodekey': '87787aeee9540ec942629b5cbf3bbcc4c765ec02129943ef7463d2864f188938'
                'username': 'root', 
                'password': 'Juzhen123!'
            }
        '''
        try:
            ip = nodedict["host"]
            nodekey = nodedict["nodekey"]
        except KeyError as e:
            raise e
        username = nodedict.get("username")
        password = nodedict.get("password")
        nodekey_file = os.path.abspath("../casedata/platon/nodekey")
        with open(nodekey_file, 'w', encoding="utf-8")as f:
            f.write(nodekey)
        if username and password:
            ssh, sftp, t = connect_linux(ip, username, password)
        else:
            # 账号密码为空时，使用默认的账号密码登录
            ssh, sftp, t = connect_linux(ip)
        # 关闭platon进程
        self.stop_platon(ssh)
        # 删除platon文件夹
        self.remove_platon(ssh)
        # 新建platon文件夹
        ssh.exec_command('mkdir ./platon')
        time.sleep(0.5)
        # 上传platon文件，并解锁
        sftp.put(self.platon, './platon/platon')
        ssh.exec_command('chmod +x ./platon/platon')
        time.sleep(0.05)
        # 根据genesis_file，判断是否需要初始化
        if genesis_file:
            remote_genesis_path = './platon/genesis.json'
            sftp.put(genesis_file, remote_genesis_path)
            # 初始化
            self.init_platon(ssh)
        else:
            ssh.exec_command('mkdir ./platon/data')
            time.sleep(0.5)
            ssh.exec_command('mkdir ./platon/data/keystore')
            time.sleep(0.5)
        # 上传cbft文件
        remote_cbft_path = './platon/data/cbft.json'
        sftp.put(self.cbft, remote_cbft_path)
        # 上传钱包文件用于挖矿
        remote_keystore = './platon/data/keystore/UTC--2018-10-04T09-02-39.439063439Z--493301712671ada506ba6ca7891f436d29185821'
        sftp.put(self.keystore, remote_keystore)
        # 根据static_node_file，判断是否需要上传该文件
        if static_node_file:
            remote_static_path = './platon/data/static-nodes.json'
            sftp.put(static_node_file, remote_static_path)
        # 上传nodekey文件
        remote_nokey_path = './platon/data/nodekey'
        sftp.put(nodekey_file, remote_nokey_path)
        # 根据 bootnodes_id的值，判断启动类型，其有值时，启动后会自动连接其他节点
        if bootnodes_id:
            start_result = self.start_platon(ssh, bootnodes_id=bootnodes_id)
        else:
            start_result = self.start_platon(ssh)
        # 根据启动后的返回结果，判断是否启动成功，如果否，尝试关闭相关端口的程序，并重试，如果多次失败，则返回异常
        if not start_result:
            self.stop_platon(ssh)
            if self.start_once > 3:
                raise Exception("节点{}无法启动".format(nodedict.get("url")))
            self.start_once += 1
            return self.start_node(nodedict, genesis_file, static_node_file, bootnodes_id)
        t.close()
        rpc_url = nodedict.get("url")
        bootnodes_id = r"enode://" + \
                       nodedict.get("id") + "@" + \
                       nodedict.get("host") + ":16789"
        return rpc_url, bootnodes_id


if __name__ == "__main__":
    auto = AutoDeployPlaton()
    auto.start_multi_node('../config/node.yml')
