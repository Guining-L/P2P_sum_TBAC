import pickle
import socket
import threading
import time
import sys


class RequestState(object):
    """docstring for simUser"""

    def __init__(self, datagram):
        self.request_id = datagram.request_id
        self.queried_peer = datagram.queried_peer

        self.Query_Datagram_Source_addr_List = []
        self.Evaluation_Datagram_List = []


class QueryDatagramList(object):
    def __init__(self, arg):
        self.arg = arg
        self.initint = 0
        self.Query_Datagram_List = []

    pass


class QueryDatagram(object):

    def __init__(self, queried_peer, request_id, send_peer_id):
        self.queried_peer = queried_peer
        self.request_id = request_id
        self.send_peer_id = send_peer_id

    pass


class EvaluationDatagram(object):
    def __init__(self, queried_peer, peer_which_initiated_query, request_id, send_peer_id):
        self.queried_peer = queried_peer
        self.peer_which_initiated_query = peer_which_initiated_query
        self.request_id = request_id
        self.send_peer_id = send_peer_id


class CredDatagram(object):
    pass



