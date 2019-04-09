from pytest_project.common.connect import connect_linux


def call_auto_build_sh(ip, username, password, sh_path):
    '''
    @Description: 用于调用自动打包的sh脚本
    @param:
        @ip:服务器ip
        @username:服务器用户名
        @password:服务器密码
        @sh_path:服务器中sh脚本的路径
    @return: bool
        @True:表示打包成功
        @False:打包失败 
    '''
    ssh, sftp, t = connect_linux(ip, username, password)
    _, out, err = ssh.exec_command('bash {}'.format(sh_path), get_pty=True)
    result = out.readlines()
    error = err.readlines()
    if error:
        raise Exception("自动打包失败-{}".format(error))
    for i in result:
        if "函数projectCompile()已执行完成,打包完成" in i:
            return True
    print(result)
    return False


if __name__ == "__main__":
    result = call_auto_build_sh(
        '192.168.9.178', 'juzhen', 'juzhen', './sss.sh')
    if not result:
        raise Exception("打包失败")
    print("打包成功")
