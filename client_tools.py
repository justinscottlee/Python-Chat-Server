import socket, _thread, pickle, time

class Packet:
    def __init__(self, key="", value=""):
        self.key = key
        self.value = value

class Message:
    def __init__(self, user_info, text):
        self.user_info = user_info
        self.text = text

class UserInfo:
    def __init__(self):
        self.id = int(time.time() * 1000)
        self.name = "noname"

class Connection:
    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        _thread.start_new_thread(self.connection_thread, ())
    
    def send_message(self, text):
        packet = Packet("send_message", text)
        packet_data = pickle.dumps(packet)
        self.socket.send(packet_data)
    
    def set_name(self, name):
        packet = Packet("set_name", name)
        packet_data = pickle.dumps(packet)
        self.socket.send(packet_data)

    def set_receive_message_function(self, function):
        """receive_message_function should take Message object as input"""
        self.receive_message_function = function

    def set_update_user_list_function(self, function):
        """user_list_function should take list of UserInfo objects as input"""
        self.update_user_list_function = function

    def connection_thread(self):
        while True:
            packet_data = self.socket.recv(2048)
            packet = pickle.loads(packet_data)
            if packet.key == "distribute_message":
                if self.receive_message_function != None:
                    self.receive_message_function(packet.value)
            elif packet.key == "distribute_user_list":
                if self.update_user_list_function != None:
                    self.update_user_list_function(packet.value)