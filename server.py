import socket
import ast
# from threading import Thread
import selectors
import types


def on_new_client(conn, addr):
    with conn:
        print(f'connected:{addr}')
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

            if user_data['message'] == '!exit':
                break

            conn.sendall(f'{user_data["name"]}: {user_data["message"]}'.encode("utf-8"))


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.sendall(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


sel = selectors.DefaultSelector()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsock:
    lsock.bind(('', 9090))
    lsock.listen()

    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

    # while True:
    #     conn, addr = s.accept()
    #     thread = Thread(target=on_new_client, args=[conn, addr])
    #     thread.run()
