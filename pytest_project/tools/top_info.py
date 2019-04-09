import os
import sys
import time
import traceback

import matplotlib
import matplotlib.pyplot as plt
import psutil

matplotlib.use("Agg")


def same(a, b):
    if len(a) != len(b):
        if len(a) > len(b):
            a.pop()
            return same(a, b)
        else:
            b.pop()
            return same(a, b)
    return a, b


def top_info(pid, path):
    pro_send = 0
    pro_recv = 0
    pro_cpu = 0
    pro_memory = 0
    i = 0
    use_time = []
    cpu_list = []
    men_list = []
    net_use_time = []
    net_send_list = []
    net_recv_list = []
    try:
        while True:
            use_time.append(i)
            net_use_time.append(i)
            cpu_lv = psutil.cpu_percent()
            print(">>>服务器cpu利用率%.2f%%" % cpu_lv)
            memory = psutil.virtual_memory()
            memory_lv = float(memory.used) / float(memory.total) * 100
            print(">>>服务器内存利用率%.2f%%" % memory_lv)
            print("======================================================")
            pro_cpu_lv = psutil.Process(pid).cpu_percent(interval=0.5)
            print("<<<当前进程cpu利用率%.2f%%" % pro_cpu_lv)
            cpu_list.append(pro_cpu_lv)
            if not pro_cpu:
                pro_cpu = pro_cpu_lv
            if pro_cpu < pro_cpu_lv:
                pro_cpu = pro_cpu_lv
            p = psutil.Process(pid)
            pro_memory_lv = p.memory_percent()
            men_list.append(pro_memory_lv)
            print("<<<当前进程内存利用率%.2f%%" % pro_memory_lv)
            print("=======================================================")
            if not pro_memory:
                pro_memory = pro_memory_lv
            if pro_memory < pro_memory_lv:
                pro_memory = pro_memory_lv
            cpu_str = "cpu:%.2f%%" % pro_cpu
            memory_str = "memory:%.2f%%" % pro_memory
            send_str = "带宽上行峰值:{}Mb/s".format(pro_send)
            recv_str = "带宽下行峰值:{}Mb/s".format(pro_recv)
            data = cpu_str + '\n' + memory_str + '\n' + send_str + '\n' + recv_str
            i += 1
            with open(path, 'w') as f:
                f.write(data)
            byte_send1 = psutil.net_io_counters().bytes_sent
            byte_recv1 = psutil.net_io_counters().bytes_recv
            time.sleep(1)
            byte_send2 = psutil.net_io_counters().bytes_sent
            byte_recv2 = psutil.net_io_counters().bytes_recv
            byte_send = byte_send2 - byte_send1
            byte_recv = byte_recv2 - byte_recv1
            bit_send = round((byte_send / 1048576) * 8, 2)
            bit_recv = round((byte_recv / 1048576) * 8, 2)
            net_send_list.append(bit_send)
            net_recv_list.append(bit_recv)
            print("<<<当前带宽上行%.2fMb/s" % bit_send)
            print("=======================================================")
            print("<<<当前带宽下行%.2fMb/s" % bit_recv)
            print("=======================================================")
            if bit_send > pro_send:
                pro_send = bit_send
            if bit_recv > pro_recv:
                pro_recv = bit_recv
    except Exception as e:
        print(e)
        traceback.extract_stack()
        print("退出运行")
    finally:
        print("当前进程最高cpu利用率%.2f%%" % pro_cpu)
        print("当前进程最高内存利用率%.2f%%" % pro_memory)
        print("带宽上行峰值:{}Mb/s".format(pro_send))
        print("带宽下行峰值:{}Mb/s".format(pro_recv))
        # print("上行list", net_send_list)
        use_time, cpu_list = same(use_time, cpu_list)
        use_time, men_list = same(use_time, men_list)
        net_use_time, net_send_list = same(net_use_time, net_send_list)
        net_use_time, net_recv_list = same(net_use_time, net_recv_list)
        fig = plt.figure(num=4, figsize=(16, 16))
        ax1 = fig.add_subplot(3, 1, 1)
        ax2 = fig.add_subplot(3, 1, 2)
        ax3 = fig.add_subplot(3, 1, 3)
        ax1.plot(use_time, cpu_list)
        ax2.plot(use_time, men_list)
        ax3.plot(net_use_time, net_send_list)
        ax3.plot(net_use_time, net_recv_list, color='red', linestyle='--')
        ax1.set_title("CPU")
        ax1.set_xlabel("time (s)")
        ax1.set_ylabel("CPU use percent (%)")
        ax2.set_title("Memory")
        ax2.set_xlabel("time (s)")
        ax2.set_ylabel("Memory use percent (%)")
        ax3.set_title("Network (upload--blue line download--red line)")
        ax3.set_xlabel("time (s)")
        ax3.set_ylabel("Network (Mb)")
        plt.legend()
        path = os.path.join(os.getcwd(), 'cpu_memory_network.png')
        plt.savefig(path)


if __name__ == '__main__':
    try:
        pid = [i for i in sys.argv][1]
    except IndexError as e:
        print("必须输入platon进程id")
        raise e
    path = os.path.abspath(os.path.join(os.getcwd(), 'top_info.log'))
    top_info(int(pid), path)