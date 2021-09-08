import socket, pickle, _thread, time

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

class User:
    def __init__(self, server, connection):
        self.user_info = UserInfo()
        self.server = server
        self.socket = connection[0]
        self.address = connection[1][0]
        self.port = str(connection[1][1])
    
    def send_packet(self, packet):
        packet_data = pickle.dumps(packet)
        self.socket.send(packet_data)

    def handle_packet(self, packet):
        if packet.key == "set_name":
            self.server.log_info("Registering name '" + packet.value + "' to ('" + self.address + "', '" + self.port + "').")
            self.user_info.name = str(packet.value)
            self.server.distribute_user_list()
        elif packet.key == "send_message":
            self.server.log_info("Received and distributing message ('" + self.user_info.name + "', '" + str(packet.value) + "').")
            message = Message(self.user_info, str(packet.value))
            self.server.distribute_message(message)

    def connection_thread(self):
        try:
            while True:
                packet_data = self.socket.recv(2048)
                packet = pickle.loads(packet_data)
                self.handle_packet(packet)
        except socket.error:
            self.server.log_info("'" + self.user_info.name + "' ('" + self.address + "', '" + self.port + "') disconnected.")
            self.server.user_list.remove(self)
            self.server.distribute_user_list()

class Server:
    def __init__(self):
        self.user_list = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("0.0.0.0", 5005))
        self.socket.listen(5)

    def log_info(self, text):
        print("[INFO] " + text)

    def distribute_user_list(self):
        user_info_list = []
        for user in self.user_list:
            user_info_list.append(user.user_info)
        packet = Packet("distribute_user_list", user_info_list)
        for user in self.user_list:
            user.send_packet(packet)

    def distribute_message(self, message):
        packet = Packet("distribute_message", message)
        for user in self.user_list:
            user.send_packet(packet)

    def start(self):
        self.log_info("Server started.")
        while True:
            self.log_info("Waiting for connections...")
            connection = self.socket.accept()
            new_user = User(self, connection)
            self.log_info("New connection from ('" + new_user.address + "', '" + new_user.port + "').")
            self.user_list.append(new_user)
            self.distribute_user_list()
            _thread.start_new_thread(new_user.connection_thread, ())

server = Server()
server.start()