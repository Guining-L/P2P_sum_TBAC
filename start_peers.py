from multiprocessing import Pool, Manager
import os, time, random
import pickle
from state import QueryDatagram, EvaluationDatagram, RequestState
import socket
import threading
import sys
from peer_control import PeerTurnOFF, ShowState


def socket_service(name, peer_addr_dict, adjace_peer):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 0))
        ip, port = s.getsockname()
        # print(type(s.getsockname()))
        # print(type(port))
        # print(str(ip)+' '+ str(port))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print("任务%s已经就绪 " % (name) + 'Waiting connection...' + str(ip) + ' ' + str(port))
    # print()
    peer_addr_dict[name] = (ip, port)

    fp = open("addr.txt", "a+", encoding="utf-8")
    try:
        fp.write(str(name) + ' ' + str(ip) + ' ' + str(port) + '\r\n')

    except Exception as e:
        print(e)
    fp.close()
    # print(type(port))
    # print(peer_addr_dict)    # 注意这里后续需要删除
    # s.close()  # 注意这里后续需要删除
    state_dict = {}
    lock = threading.Lock()
    thr_start_times = 0
    while 1:
        try:
            '''在启动一个子线程后，主线程会直接在accept上等待，此时套接字若未完全关闭，会导致下一个子进程继续启动'''
            conn, addr = s.accept()
            thr_start_times += 1
            # print(thr_start_times)
        except Exception as e:
            print("accept出错了！" + str(e))
            print('accept出错了！' + str(thr_start_times))
            return
        else:
            # print('在return之后！！')
            print('thr_start_times ' + str(thr_start_times))

            t = threading.Thread(target=receive_and_send_data_gram, name=thr_start_times,
                                 args=(conn, addr, state_dict, lock, peer_addr_dict, name, s, adjace_peer,))
            t.start()


def receive_and_send_data_gram(conn, addr, state_dict, lock, peer_addr_dict, peer_name, peer_socket, adjace_peer):
    # print(str(threading.get_ident()) + '对应的名字是' + str(threading.current_thread().name))
    # print('线程内输出：Run task %s (%s)...直连节点是' % (peer_name, os.getpid()) + str(adjace_peer))
    print('Accept new connection from {0}\n'.format(addr), end='')
    # print(type(addr))
    conn.send(('Hi, Welcome to the server!').encode())

    recv_message = conn.recv(1024)
    recv_object = pickle.loads(recv_message)

    try:
        conn.close()
        pass
    except Exception as e:
        print(e)

    print(type(recv_object))
    if type(recv_object) == QueryDatagram:
        lock.acquire()
        first_time_flag = (recv_object.request_id not in state_dict)
        if first_time_flag:
            state_dict[recv_object.request_id] = RequestState(recv_object)
        lock.release()
        # 将发送这个查询报文的来源节点记录
        (state_dict[recv_object.request_id]).Query_Datagram_Source_Peer_List.append(recv_object.send_peer_id)
        print('发送这个查询报文的是' + str(recv_object.send_peer_id))
        if first_time_flag:
            # 给非来源直连节点转发，所有的处理与发送由第一次收到报文的线程来做
            if (state_dict[recv_object.request_id].queried_peer) in adjace_peer:
                # 如果被查找的节点是当前节点的直连节点，则停止发送查询报文，直接向回转发评价报文即可
                pass
            else:
                for peer in adjace_peer:
                    # 在当前节点的所有直连节点中
                    if peer not in (state_dict[recv_object.request_id]).Query_Datagram_Source_Peer_List:
                        # 如果直连节点是非来源节点

                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                            peer_addr = peer_addr_dict[peer]

                            print('要将查询报文发送给：', peer_addr)
                            s.connect(peer_addr)
                        except socket.error as msg:
                            print(msg)
                            sys.exit(1)

                        # a = QueryDatagram('A', 1234577778888, 4)
                        new_query_datagram = QueryDatagram(recv_object.queried_peer, recv_object.request_id, peer_name)
                        #转发要重新生成一个对象，直接转发recv_object的话下一个节点识别不出对象类型来
                        s.send(pickle.dumps(new_query_datagram))
                        (state_dict[recv_object.request_id]).Query_Datagram_Destination_Peer_List.append(
                            peer)#记录向外转发的目的节点
                        s.close()

                        pass

    if type(recv_object) == EvaluationDatagram:
        lock.acquire()
        try:
            first_time_recv_eva_flag = 0
            if not (state_dict[recv_object.request_id]).Evaluation_Datagram_List:
                first_time_recv_eva_flag = 1
            (state_dict[recv_object.request_id]).Evaluation_Datagram_List.append(recv_object)
            print("收到评估报文！")
        except Exception as e:
            print("没有对应的会话状态！", e)
        lock.release()
        print("该评估报文是第一次收到", first_time_recv_eva_flag)
        # if 1:
        if first_time_recv_eva_flag:
            # 所有的处理与发送由第一次收到报文的线程来做
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                first_peer = (state_dict[recv_object.request_id].Query_Datagram_Source_Peer_List)[0]
                first_peer_addr = peer_addr_dict[first_peer]

                print('第一个收到查询报文的是：', first_peer_addr)
                s.connect(first_peer_addr)
            except socket.error as msg:
                print(msg)
                sys.exit(1)

            new_eval_datagram = EvaluationDatagram(recv_object.queried_peer, recv_object.request_id, peer_name,
                                   recv_object.peer_which_initiated_query)
            s.send(pickle.dumps(new_eval_datagram))
            pass

    if type(recv_object) == PeerTurnOFF:
        print('进程' + str(peer_name) + '收到关闭')
        try:
            peer_socket.shutdown(0)
            peer_socket.close()
            # conn.close()
            # sys.exit(1)
        except Exception as e:
            print(e)
        print('进程' + str(peer_name) + '已关闭')

    if type(recv_object) == ShowState:

        print("当前peer name" + str(peer_name))
        print("会话状态字典", state_dict)
        for id, state_object in state_dict.items():
            try:
                print("当前会话ID", state_object.request_id)
                print("这个会话状态被查询的节点", state_object.queried_peer)
                print("查询报文来源列表", state_object.Query_Datagram_Source_Peer_List)
                print("查询报文转发目的节点列表", state_object.Query_Datagram_Destination_Peer_List)
                print("当前会话评估报文列表", state_object.Evaluation_Datagram_List)

            except Exception as e:
                print(e)

    # conn.close()

    return


def deal_data(conn, addr):
    print('Accept new connection from {0}'.format(addr))
    conn.send(('Hi, Welcome to the server!').encode())
    while 1:
        data = conn.recv(1024)
        print('{0} client send data is {1}'.format(addr,
                                                   data.decode()))  # b'\xe8\xbf\x99\xe6\xac\xa1\xe5\x8f\xaf\xe4\xbb\xa5\xe4\xba\x86'
        time.sleep(1)
        if data == 'exit' or not data:
            print('{0} connection close'.format(addr))
            conn.send(('Connection closed!').encode(encoding='UTF-8'))
            break
        conn.send(bytes('Hello, {0}'.format(data), "UTF-8"))  # TypeError: a bytes-like object is required, not 'str'
    conn.close()


def long_time_task(name, d, adjace_peer):
    try:
        print('Run task %s (%s)...直连节点是' % (name, os.getpid()) + str(adjace_peer))
        # d[name]=name
        # print(d[name])
        start = time.time()
        # time.sleep(random.random() * 3)
        socket_service(name, d, adjace_peer)

        end = time.time()
        print('Task %s runs %0.2f seconds.' % (name, (end - start)))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    print('Parent process %s.' % os.getpid())
    p = Pool(200)
    mgr = Manager()
    d = mgr.dict()

    adjace_list = [
        [1, 2],
        [0, 2, 3],
        [0, 1, 3],
        [1, 2],
    ]

    try:
        fp = open("addr.txt", "w", encoding="utf-8")

    except Exception as e:
        print(e)
    else:
        fp.close()

    for i in range(4):
        p.apply_async(long_time_task, args=(i, d, adjace_list[i]))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print(d)
    print('All subprocesses done.')
