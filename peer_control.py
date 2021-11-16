import socket
import sys
import pickle
import time


class PeerTurnOFF(object):
    def __init__(self, ):
        turn_off = 1


def load(filename):
    data = {}
    file = open(filename, 'r')
    for line in file.readlines():
        line = line.strip('\n')  # 除去换行
        line = line.split(' ')  # 文件以“ ”分隔
        if "" in line:  # 解决每行结尾有空格的问题
            line.remove("")
        data[int(line[0])] = (line[1], int(line[2]))
        # print(line)
    file.close()
    return data


def send_OFF_datagram(addr_list):
    for id, addr in addr_list.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(addr)
        except socket.error as msg:
            print(msg)
            sys.exit(1)
        print(s.recv(1024))  # 目的在于接受：Accept new connection from (...
        b = PeerTurnOFF()
        s.send(pickle.dumps(b))
        s.close()



if __name__ == '__main__':
    print(load('addr.txt'))
    send_OFF_datagram(load('addr.txt'))


