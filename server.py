import socket
import ast


sock = socket.socket()
sock.bind(('', 9090))

sock.listen(1)
conn, addr = sock.accept()
print(f'connected:{addr}')

# users = []

while True:
    data = conn.recv(1024)
    data_bytes = data.decode("UTF-8")
    user_data = ast.literal_eval(data_bytes)

    if not isinstance(user_data, dict):
        conn.send(b'Bad request\n')
        continue

    if len(list(user_data.keys())) == 2:
        if 'name' not in list(user_data.keys()) or 'message' not in list(user_data.keys()):
            conn.send(b'Bad request\n')
            continue
    else:
        conn.send(b'Bad request\n')
        continue

    # if user_data['name'] not in users or user_data['name'] == 'unknown':
    #     conn.send(b'Unknown user. Please sign up!\n Enter your name:')
    #     continue
    # else:
    #     users.append(user_data['name'])

    # print(users)
    if user_data['message'] == '!exit':
        break

    conn.send(f'{user_data["name"]}: {user_data["message"]}'.encode("utf-8"))

conn.close()
