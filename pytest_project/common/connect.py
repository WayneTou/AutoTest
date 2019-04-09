
import paramiko
from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware


def connect_web3(url):
    '''
    连接web3服务,增加区块查询中间件,用于实现eth_getBlockByHash,eth_getBlockByNumber等方法
    '''
    w3 = Web3(HTTPProvider(url))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    return w3


def connect_linux(ip, username='root', password='Juzhen123!'):
    '''
    连接linux服务器
    params:
        @ip:服务器ip
        @username:用户名
        @password:密码
    return:
        @ssh:ssh实例，用于执行命令 ssh.exec_command(cmd)
        @sftp:文件传输实例，用于上传下载文件 sftp.get(a,b)将a下载到b,sftp.put(a,b)把a上传到b
        @t:连接实例，用于关闭连接 t.close()
    '''
    t = paramiko.Transport((ip, 22))
    t.connect(username=username, password=password)
    ssh = paramiko.SSHClient()
    ssh._transport = t
    sftp = paramiko.SFTPClient.from_transport(t)
    return ssh, sftp, t
