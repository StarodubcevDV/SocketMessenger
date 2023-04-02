import socket
import time
import ast

ROOMS = []


class Room:
    def __init__(self, name, sock_):
        self.room_name = name
        self.user_list = {}
        self.sock = sock_

    def get_name(self):
        return self.room_name

    def get_users_names(self):
        return list(self.user_list.keys())

    def get_users_addresses(self):
        return list(self.user_list.values())

    def add_user(self, user_name, user_address):
        self.user_list[user_name] = user_address
        cur_time = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
        connection_data = f'{user_name} connected at {cur_time}'.encode('UTF-8')
        self.send_data_to_all_users(user_address, connection_data)
        print(connection_data.decode('UTF-8'))

    def disconnect_user(self, user_name):
        if len(self.get_users_names()) - 1 != 0:
            cur_time = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
            connection_data = f'{user_name} disconnected at {cur_time}'.encode('UTF-8')
            self.send_data_to_all_users(self.user_list[user_name], connection_data)
        del self.user_list[user_name]

    def send_data_to_all_users(self, sender, data_to_send):
        for user in self.get_users_addresses():
            if sender != user:
                self.sock.sendto(data_to_send, user)


def parse_received_data(received_data):
    decoded_data = received_data.decode('UTF-8')
    return ast.literal_eval(decoded_data)


def create_response(decoded_data):
    return f'{decoded_data["name"]}: {decoded_data["message"]}'.encode('UTF-8')


def chatting(room_, parsed_data, user_addr_):
    try:
        if parsed_data['message'] == '!exit':
            room_.disconnect_user(parsed_data['name'])
        elif parsed_data['message'] == '!users':
            users_data = f'{room_.get_users_names()}'.encode('UTF-8')
            room_.sock.sendto(users_data, user_addr_)
        else:
            room_.send_data_to_all_users(user_addr_, create_response(parsed_data))
    except:
        print("Room stopped")
        return -1


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 9090))

    while True:
        data, user_addr = sock.recvfrom(1024)

        parsed_data = parse_received_data(data)

        if parsed_data['message'] == '!create' or parsed_data['message'] == '!connect':
            if parsed_data['room'] not in [room_.get_name() for room_ in ROOMS]:
                ROOMS.append(Room(parsed_data['room'], sock))
                ROOMS[-1].add_user(parsed_data['name'], user_addr)
                sock.sendto('created'.encode('UTF-8'), user_addr)
                # chatting(ROOMS[-1], parsed_data, user_addr)
            else:
                room = ROOMS[[room_.get_name() for room_ in ROOMS].index(parsed_data['room'])]
                if parsed_data['name'] not in room.get_users_names():
                    room.add_user(parsed_data['name'], user_addr)
                    sock.sendto('connected'.encode('UTF-8'), user_addr)
                    # chatting(room, parsed_data, user_addr)
        else:
            room = ROOMS[[room_.get_name() for room_ in ROOMS].index(parsed_data['room'])]
            chatting(room, parsed_data, user_addr)
