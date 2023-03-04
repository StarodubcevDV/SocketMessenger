import re
import socket
import json


class User:
    def __init__(self, name):
        self.__name = name
        self._current_room = None
        # self._rooms = {}

    def connect_room(self, room):
        self._current_room = socket.socket()

        if not re.match(r"[a-z]*:\d*", room):
            raise Exception('Invalid room address!')

        room_address = room.split(":")[0]
        room_port = int(room.split(":")[1])

        try:
            self._current_room.connect((room_address, room_port))
        except:
            raise Exception('Something went wrong, cant connect to the room.\n')
        print(f'Successful connection to {room}')
        # self._rooms['room'] = self._current_room

    def chatting(self):
        print('Start messaging: ')
        while True:
            message = input()

            message_dict = {'name': self.__name, 'message': message}
            user_encode_message = json.dumps(message_dict).encode('utf-8')
            try:
                self._current_room.send(user_encode_message)
            except:
                print("Sorry, cant send the message.")
                continue

            server_response = self._current_room.recv(1024)
            server_response_message = server_response.decode("utf-8")

            print("Server > " + server_response_message)

            if message == '!exit':
                self.disconnect_room()
                return 0

    def disconnect_room(self):
        self._current_room.close()
        print(f'Disconnected')
        self._current_room = None


if __name__ == '__main__':
    name = input('Enter your name: ')
    user = User(name)

    connect = False
    while not connect:
        try:
            room_address = input('Enter room address: ')
            user.connect_room(room_address)
            connect = True
        except Exception as e:
            print(e)
            connect = False
    user.chatting()
