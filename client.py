import re
import socket
import json
import threading
import time

SERVER_ADDRESS = ('localhost', 9090)


class User:
    def __init__(self, name_):
        self.__name = name_
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 0))
        # self.sock.setblocking(False)
        self._current_room = None
        self._rooms = []

    def connect_room(self, room):
        self._current_room = room
        self._rooms.append(self._current_room)

    def receive_msg(self):
        while True:
            server_response, addr = self.sock.recvfrom(1024)
            server_response_message = server_response.decode("utf-8")
            print("Server > " + server_response_message)
            time.sleep(0.1)

    def chatting(self):
        receiving_thread = threading.Thread(target=self.receive_msg)
        receiving_thread.start()
        print('Start messaging: ')
        while True:
            message = input()

            message_dict = {'name': self.__name, 'message': message}
            user_encode_message = json.dumps(message_dict).encode('utf-8')

            try:
                self.sock.sendto(user_encode_message, SERVER_ADDRESS)
            except:
                print("Sorry, cant send the message.")
                continue

            if message == '!exit':
                self.disconnect_room()
                receiving_thread.join()
                return 0

    def create_room(self, room_name):
        self._current_room = room_name

    def disconnect_room(self):
        print(f'Disconnected')
        self._current_room = None


if __name__ == '__main__':
    name = input('Enter your name: ')
    user = User(name)

    while True:
        try:
            option = input('[connect] the existing room or [create] your own:')
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

