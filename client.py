import socket
import json
import time
import random
import multiprocessing


SERVER_ADDRESS = ('localhost', 9090)

STOP_RECEIVING = False


def receive_msg(sock_):
    while True:
        server_response, addr = sock_.recvfrom(1024)
        server_response_message = server_response.decode("utf-8")
        print("Server > " + server_response_message)
        time.sleep(0.1)


class User:
    def __init__(self, name_):
        self.__name = name_
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", random.randint(0, 500)))   # Problem in socket port (same for all)
        self._current_room = None
        self._rooms = []

    def get_rooms(self):
        return self._rooms

    def chatting(self):
        receiving_thread = multiprocessing.Process(target=receive_msg, args=(self.sock,))
        receiving_thread.start()
        print('Start messaging: ')
        while True:
            message = input()

            message_dict = {'name': self.__name, 'room': self._current_room, 'message': message}
            user_encode_message = json.dumps(message_dict).encode('utf-8')

            try:
                self.sock.sendto(user_encode_message, SERVER_ADDRESS)
            except:
                print("Sorry, cant send the message.")
                continue

            if message == '!exit':
                self.disconnect_room()
                receiving_thread.terminate()
                return 0

    def create_room(self, room_name):
        message_dict = {'name': self.__name, 'room': room_name, 'message': '!create'}
        user_encode_message = json.dumps(message_dict).encode('utf-8')
        self.sock.sendto(user_encode_message, SERVER_ADDRESS)

        server_response, addr = self.sock.recvfrom(1024)
        server_response_message = server_response.decode("utf-8")
        if server_response_message == 'created':
            self._rooms.append(self._current_room)
            print(f'{room_name} created!')
        elif server_response_message == 'connected':
            print('Room with the same name already exist, connecting.')
        self._current_room = room_name

    def connect_room(self, room_name):
        message_dict = {'name': self.__name, 'room': room_name, 'message': '!connect'}
        user_encode_message = json.dumps(message_dict).encode('utf-8')
        self.sock.sendto(user_encode_message, SERVER_ADDRESS)
        server_response, addr = self.sock.recvfrom(1024)
        server_response_message = server_response.decode("utf-8")

        if server_response_message == 'connected':
            print(f'Connected to {room_name}!')
        elif server_response_message == 'created':
            self._rooms.append(room_name)
            print('Room with the same name doesnt exist, creating.')
        self._current_room = room_name

    def disconnect_room(self):
        print(f'Disconnected from {self._current_room}')
        self._current_room = None


if __name__ == '__main__':
    name = input('Enter your name: ')
    user = User(name)

    while True:
        try:
            option = input('[connect] the existing room or [create] your own: ')
            if option == 'connect':
                room_address = input('Enter room name: ')
                user.connect_room(room_address)
                user.chatting()
            elif option == 'create':
                room_address = input('Enter room name: ')
                user.create_room(room_address)
                user.chatting()
        except Exception as e:
            print(e)
            continue

