import socket
import time
import threading
from itertools import groupby


def response_func(data: str) -> str:
    """
    Функция вызывается при необходимости ответа на данные, посланные экспериментальной установкой. В нее добавляется
    необходимая логика.

    :param data: строка данных, полученных от экспериментальной установки

    :return: строка, которую нужно будет отправить экспериментальной установке
    """
    print(data)
    resp = input("input: ")
    return resp


def online_check(client_socket: socket.socket):
    """
    Функция проверки сокета на доступность. Посылает знак &, который на принимающей стороне необходимо отфильтровывать

    :param client_socket: проверяемый сокет
    :return:
    """
    try:
        client_socket.send("&".encode('utf-8'))
        return True
    except ConnectionResetError:
        return False


class Client:
    """
    Класс клиента
    """
    def __init__(self):
        self.zero_time = time.time()
        self.server_ip = '192.168.43.150'
        self.server_port = 5556

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        self.server_socket.send('-=-nm-=-first message from client'.encode('utf-8'))

    def connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        socket_connected_ = False
        while not socket_connected_:
            try:
                self.server_socket.connect((self.server_ip, self.server_port))
                socket_connected_ = True
                threading.Thread(target=self.main_loop, args=(self.server_socket,)).start()
            except socket.error:
                print('Server is offline. Retrying in 10 seconds')
                time.sleep(10)

    def main_loop(self, server_socket_: socket.socket):
        try:
            resp = response_func("first msg")
            server_socket_.send(f"-=-nm-=-{resp}".encode('utf-8'))
        except socket.error:
            self.connect(server_socket_)

        while True:
            try:
                data = '&'
                while [el for el, _ in groupby(sorted(data.split('&')))] == ['']:
                    data = self.server_socket.recv(1024).decode('utf-8')

                try:
                    data_array = data.split("-=-")[1::]
                    if data_array[0] == 'main':
                        ans = response_func(data_array[1])
                        server_socket_.send(
                            f"-=-nm-=-time: {round(time.time() - self.zero_time)}s, ans: {ans}".encode('utf-8'))
                    else:
                        print(f"{data_array[0]}: {data_array[1]}")
                        pass
                except ValueError:
                    print(f"error occurred: {data.split('-=-')}")
            except ConnectionResetError:
                self.connect()


if __name__ == "__main__":
    Client()
