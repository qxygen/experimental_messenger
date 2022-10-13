import socket
import time
import threading
from itertools import groupby


def response_func(data) -> str:
    print(data)
    resp = input("input: ")
    return resp


def online_check(client_socket: socket.socket):
    try:
        client_socket.send("&".encode('utf-8'))
        # print(f"online check client {client_socket}: true")
        return True
    except ConnectionResetError:
        # print(f"online check client {client_socket}: false")
        return False


class Client:
    def __init__(self):
        self.zero_time = time.time()
        self.server_ip = '192.168.43.150'
        self.server_port = 5556

        self.server_socket = 0
        self.connect()
        # self.server_socket.send('-=-main-=-first message from main client'.encode('utf-8'))

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
                # print('.')
                data = '&'
                # data = server_socket_.recv(1024).decode('utf-8')
                while [el for el, _ in groupby(sorted(data.split('&')))] == ['']:
                    data = self.server_socket.recv(1024).decode('utf-8')
                    # print("while ", data)
                # data = data
                # print(data.split("-=-")[1::])
                data_array = data.split("-=-")[1::]
                if data_array[0] == 'nm':
                    ans = response_func(data_array[1])
                    server_socket_.send(f"-=-main-=-time: {round(time.time() - self.zero_time)}s, ans: {ans}".encode('utf-8'))
                else:
                    print(f"{data_array[0]}: {data_array[1]}")
                    pass
                # except ValueError:
                    # print(f"error occured: {data.split('-=-')}")

            except ConnectionResetError:
                self.connect()


if __name__ == "__main__":
    Client()