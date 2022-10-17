import socket
import time
import threading
from itertools import groupby

zero_time = time.time()


def clean_data(s: str, symbol='&'):
    pos = s.find(symbol)
    while pos != -1:
        s[:] = s[:pos] + s[pos + 1:]
        pos = s.find(symbol)
    return s


def response_func(data) -> str:
    print(f"client: {data}")
    resp = input("input: ")
    return f"-=-main-=-time: {round(time.time() - zero_time)}s, ans: {resp}"


def online_check(client_socket: socket.socket):
    try:
        client_socket.send("&".encode('utf-8'))

        return True
    except ConnectionResetError:

        return False


class Client:
    def __init__(self):
        self.zero_time = zero_time
        self.server_ip = '192.168.111.89'
        self.server_port = 5556

        self.server_socket = 0
        self.connect()

    def connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        socket_connected_ = False
        print("connect")
        while not socket_connected_:
            try:
                self.server_socket.connect((self.server_ip, self.server_port))
                socket_connected_ = True
                print("connected to server")
                self.server_socket.send('-=-main-=-first message from main client'.encode('utf-8'))
                threading.Thread(target=self.main_loop, args=(self.server_socket,)).start()
            except socket.error:
                print('Server is offline. Retrying in 10 seconds')
                time.sleep(10)

    def main_loop(self, server_socket_: socket.socket):
        while True:
            try:
                data = '&'

                while [el for el, _ in groupby(sorted(data.split('&')))] == ['']:
                    data = self.server_socket.recv(1024).decode('utf-8')
                data = clean_data(data)
                data_array = data.split("-=-")[1::]
                if data_array[0] == 'nm':
                    ans = response_func(data_array[1])
                    server_socket_.send(ans.encode('utf-8'))

                else:
                    print(f"{data_array[0]}: {data_array[1]}")
                    pass

            except ConnectionResetError:
                self.connect()


if __name__ == "__main__":
    Client()
