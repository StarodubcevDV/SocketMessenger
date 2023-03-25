import socket
import time
import json
import ast


USERS_LIST = []


def send_data_to_all_users(sock_send, sender, data_to_send):
    for user in USERS_LIST:
        if sender != user:
            sock_send.sendto(data_to_send, user)


def parse_received_data(received_data):
    decoded_data = received_data.decode('UTF-8')
    return ast.literal_eval(decoded_data)


def create_response(decoded_data):
    return f'{decoded_data["name"]}: {decoded_data["message"]}'.encode('UTF-8')


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 9090))

    while True:
        try:
            data, user_addr = sock.recvfrom(1024)

            if user_addr not in USERS_LIST:
                USERS_LIST.append(user_addr)
                cur_time = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
                connection_data = f'{parse_received_data(data)["name"]} connected at {cur_time}'.encode('UTF-8')
                send_data_to_all_users(sock, user_addr, connection_data)
                print(connection_data.decode('UTF-8'))

            if parse_received_data(data)['message'] == '!exit':
                print('ololo disc')
                USERS_LIST.remove(user_addr)
                cur_time = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
                connection_data = f'{parse_received_data(data)["name"]} disconnected at {cur_time}'.encode('UTF-8')
                send_data_to_all_users(sock, user_addr, connection_data)
            elif parse_received_data(data)['message'] == '!users':
                users_data = f'{USERS_LIST}'.encode('UTF-8')
                sock.sendto(users_data, user_addr)
            else:
                send_data_to_all_users(sock, user_addr, create_response(parse_received_data(data)))
        except:
            print("Server stopped")
            break
