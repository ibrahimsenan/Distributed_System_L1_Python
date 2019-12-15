# coding=utf-8
import argparse
import json
import sys
from threading import Lock, Thread
import time
import traceback
import bottle
from bottle import Bottle, request, template, run, static_file
import requests


# ------------------------------------------------------------------------------------------------------

class Blackboard():

    def __init__(self):
        self.content = []
        self.lock = Lock()  # use lock when you modify the content

    def get_content(self):
        with self.lock:
            cnt = self.content
        return cnt

    def set_content(self, new_content, post_type):
        with self.lock:
            if post_type == 0:
                self.content.append(new_content)
            else:
                self.content = new_content
        return


# ------------------------------------------------------------------------------------------------------
class Server(Bottle):

    def __init__(self, ID, IP, servers_list):
        super(Server, self).__init__()
        self.blackboard = Blackboard()
        self.id = int(ID)
        self.ip = str(IP)
        self.servers_list = servers_list
        # list all REST URIs
        # if you add new URIs to the server, you need to add them here
        self.route('/', callback=self.index)
        self.get('/board', callback=self.get_board)
        self.post('/board', callback=self.post_index)
        self.post('/board_concurrent', callback=self.post_concurrent)
        self.post('/board_concurrent/<id:int>/', callback=self.modify_concurrent)
        self.post('/propagate', callback=self.post_propagate)
        self.post('/propagate/<id:int>/modify/', callback=self.post_propagate_modify)
        self.post('/propagate/<id:int>/delete/', callback=self.post_propagate_delete)
        self.post('/board/<id:int>/', callback=self.post_board)
        # we give access to the templates elements
        self.get('/templates/<filename:path>', callback=self.get_template)
        # You can have variables in the URI, here's an example
        # self.post('/board/<element_id:int>/', callback=self.post_board) where post_board takes an argument (integer) called element_id

    def do_parallel_task(self, method, args=None):
        # create a thread running a new task
        # Usage example: self.do_parallel_task(self.contact_another_server, args=("10.1.0.2", "/index", "POST", params_dict))
        # this would start a thread sending a post request to server 10.1.0.2 with URI /index and with params params_dict
        thread = Thread(target=method,
                        args=args)
        thread.daemon = True
        thread.start()

    def do_parallel_task_after_delay(self, delay, method, args=None):
        # create a thread, and run a task after a specified delay
        # Usage example: self.do_parallel_task_after_delay(10, self.start_election, args=(,))
        # this would start a thread starting an election after 10 seconds
        thread = Thread(target=self._wrapper_delay_and_execute,
                        args=(delay, method, args))
        thread.daemon = True
        thread.start()

    def _wrapper_delay_and_execute(self, delay, method, args):
        time.sleep(delay)  # in sec
        method(*args)

    def contact_another_server(self, srv_ip, URI, itemID, update_option, req='POST', params_dict=None):
        # Try to contact another serverthrough a POST or GET
        # usage: server.contact_another_server("10.1.1.1", "/index", "POST", params_dict)
        success = False
        itemToSend = self.blackboard.get_content()
        try:
            if itemID != -1:
                if 'POST' in req:
                    res = requests.post('http://{}{}{}/{}/'.format(srv_ip, URI, itemID, update_option),
                                        data=itemToSend[itemID])
                    print(res)
                elif 'GET' in req:
                    res = requests.get('http://{}{}{}/{}/'.format(srv_ip, URI, itemID, update_option))
            else:
                if 'POST' in req:
                    res = requests.post('http://{}{}'.format(srv_ip, URI),
                                        data=itemToSend[itemID])
                elif 'GET' in req:
                    res = requests.get('http://{}{}'.format(srv_ip, URI))
            # result can be accessed res.json()
            if res.status_code == 200:
                success = True
        except Exception as e:
            print("[ERROR] " + str(e))
        return success

    def propagate_to_all_servers(self, URI, itemID, update_option, req='POST', params_dict=None):
        for srv_ip in self.servers_list:
            #print(srv_ip, self.ip)
            if srv_ip != self.ip:  # don't propagate to yourself
                success = self.contact_another_server(srv_ip, URI, itemID, update_option, req, params_dict=None)
                if not success:
                    print("[WARNING ]Could not contact server {}".format(srv_ip))

    # route to ('/')
    def index(self):
        # we must transform the blackboard as a dict for compatiobility reasons
        board = dict()
        board["0"] = self.blackboard.get_content()
        return template('server/templates/index.tpl',
                        board_title='Server {} ({})'.format(self.id,
                                                            self.ip),
                        board_dict=board.iteritems(),
                        members_name_string='Alsaeedi Sarah, Ibrahim Senan')

    # get on ('/board')
    def get_board(self):
        # we must transform the blackboard as a dict for compatibility reasons
        board = dict()
        contentA = self.blackboard.get_content()
        for i in range(len(contentA)):
            board["%s" % i] = contentA[i]
        # board = sorted(board.keys())
        return template('server/templates/blackboard.tpl',
                        board_title='Server {} ({})'.format(self.id,
                                                            self.ip),
                        board_dict=board.iteritems())

    # post on ('/')
    def post_index(self):
        try:
            # we read the POST form, and check for an element called 'entry'
            new_entry1 = request.body.read()
            new_entry = request.forms.get('entry')
            print("Received: {}".format(new_entry1))
            self.blackboard.set_content(new_entry, 0)
            itemID = -1
            updateO = None
            self.propagate_to_all_servers("/propagate", itemID, updateO, "POST", params_dict=None)
        except Exception as e:
            print("[ERROR] " + str(e))

    # post on ('/board_concurrent')
    def post_concurrent(self):
        try:
            # we read the POST form, and check for an element called 'entry'
            new_entry = request.body.read()
            print("Received: {}".format(new_entry))
            self.blackboard.set_content(new_entry, 0)
        except Exception as e:
            print("[ERROR] " + str(e))

    # post on ('/propagate')
    def post_propagate(self):
        try:
            # we read the POST form, and check for an element called 'entry'
            new_entry = request.body.read()
            print("Received: {}".format(new_entry))
            self.blackboard.set_content(new_entry, 0)
        except Exception as e:
            print("[ERROR] " + str(e))

    def post_propagate_modify(self, id):
        try:
            # we read the POST form, and check for an element called 'entry'
            new_entry = request.body.read()
            x = new_entry.split('&')
            contentA = self.blackboard.get_content()
            contentA[id] = x[0]
            self.blackboard.set_content(contentA, 1)
        except Exception as e:
            print("[ERROR] " + str(e))

    def post_propagate_delete(self, id):
        try:
            # we read the POST form, and check for an element called 'entry'
            contentA = self.blackboard.get_content()
            print(str(len(contentA)))
            del contentA[id]
            self.blackboard.set_content(contentA, 1)
        except Exception as e:
            print("[ERROR] " + str(e))

    # post on ('/board/element_Id')
    def post_board(self, id):
        try:
            print("ENTER BORDER", str(id))
            new_entry = request.forms.get('entry')
            update_option = request.forms.get('update')
            print("ENTER BORDER XX", str(update_option))
            contentA = self.blackboard.get_content()
            itemID = int(id)
            contentA[id] = new_entry
            self.propagate_to_all_servers("/propagate/", itemID, update_option, "POST", params_dict=None)
            if update_option == "delete":
                del contentA[id]
            self.blackboard.set_content(contentA, 1)
        except Exception as e:
            print("[ERROR]" + str(e))

    # post on ('/board_concurrent/element_Id')
    def modify_concurrent(self, id):
        try:
            new_entry = request.body.read()
            contentA = self.blackboard.get_content()
            contentA[id] = new_entry
            self.blackboard.set_content(contentA, 1)
        except Exception as e:
            print("[ERROR]" + str(e))

    def get_template(self, filename):
        return static_file(filename, root='./server/templates/')


# ------------------------------------------------------------------------------------------------------
def main():
    PORT = 80
    parser = argparse.ArgumentParser(description='Your own implementation of the distributed blackboard')
    parser.add_argument('--id',
                        nargs='?',
                        dest='id',
                        default=1,
                        type=int,
                        help='This server ID')
    parser.add_argument('--servers',
                        nargs='?',
                        dest='srv_list',
                        default="10.1.0.1,10.1.0.2",
                        help='List of all servers present in the network')
    args = parser.parse_args()
    server_id = args.id
    server_ip = "10.1.0.{}".format(server_id)
    servers_list = args.srv_list.split(",")

    try:
        server = Server(server_id,
                        server_ip,
                        servers_list)
        bottle.run(server,
                   host=server_ip,
                   port=PORT)
    except Exception as e:
        print("[ERROR] " + str(e))


# ------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
