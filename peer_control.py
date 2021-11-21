import socket
import sys
import pickle
import time
from state import QueryDatagram, EvaluationDatagram, RequestState


class PeerTurnOFF(object):
    def __init__(self, ):
        turn_off = 1


class ShowState(object):
    def __init__(self, ):
        show = 1


def load(filename):
    addr_list = {}
    file = open(filename, 'r')
    for line in file.readlines():
        line = line.strip('\n')  # 除去换行
        line = line.split(' ')  # 文件以“ ”分隔
        if "" in line:  # 解决每行结尾有空格的问题
            line.remove("")
        addr_list[int(line[0])] = (line[1], int(line[2]))
        # print(line)
    file.close()
    return addr_list


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


def send_show_state_datagram_to_all_peer(addr_list):
    for id, addr in addr_list.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(addr)
        except socket.error as msg:
            print(msg)
            sys.exit(1)
        print(s.recv(1024))  # 目的在于接受：Accept new connection from (...
        b = ShowState()
        s.send(pickle.dumps(b))
        s.close()
        time.sleep(1)


def send_show_state_datagram_to_a_peer(addr_list, key):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr_list[key])
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print(s.recv(1024))  # 目的在于接受：Accept new connection from (...
    b = ShowState()
    s.send(pickle.dumps(b))
    s.close()

def send_query_datagram_to_a_peer(addr_list, key, queried_peer,request_id, send_peer_id):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr_list[key])
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print(s.recv(1024))  # 目的在于接受：Accept new connection from (...
    b = QueryDatagram(queried_peer,request_id, send_peer_id)
    s.send(pickle.dumps(b))
    s.close()


if __name__ == '__main__':
    print(load('addr.txt'))
    # send_OFF_datagram(load('addr.txt'))
    addr_list = load('addr.txt')
    # send_show_state_datagram_to_a_peer(addr_list, 1)
    send_show_state_datagram_to_all_peer(addr_list)
    # send_query_datagram_to_a_peer(addr_list, 3, 0, 1234577778888, 4)
