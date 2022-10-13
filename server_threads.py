import time
import socket
import threading
from itertools import groupby


def online_check(client_socket: socket.socket):
    try:
        client_socket.send("&".encode('utf-8'))
        # print(f"online check client {client_socket}: true")
        return True
    except ConnectionResetError:
        # print(f"online check client {client_socket}: false")
        return False
    except AttributeError:
        # print(f"online check client {client_socket}: false")
        return False


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.main_client = ()
        self.main_client_available_status = True
        self.client = ()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(0)
        threading.Thread(target=self.connect).start()

        print(f'Listening at {self.ip}:{self.port}')

    def connect(self):
        """
        Подлючнеие новых пользователей, запускаемое из потока
        """
        while True:
            client, address = self.server.accept()
            print(f'Connected: {client.getpeername()}')
            self.check_user_data(client)
            time.sleep(1)

    def check_user_data(self, client_socket: socket.socket):
        try:
            data = client_socket.recv(1024)
            print(data.decode('utf-8').split('-=-')[1::])
            [nick, msg] = data.decode('utf-8').split('-=-')[1::]
            print(nick, msg)
            if nick == 'main':
                self.main_client = client_socket
                threading.Thread(target=self.main_message_handler, args=(client_socket,)).start()
            elif nick == 'nm':
                if self.main_client_available_status:
                    self.client = client_socket
                    client_socket.send("-=-server-=-You are connected to the server successfully".encode('utf-8'))
                    if online_check(self.main_client):
                        print("online")
                        client_socket.send("-=-server-=-You are connected to the main client successfully".encode('utf-8'))
                    else:
                        print("offline")
                        client_socket.send("-=-server-=-The main client is currently offline. Try again later".encode('utf-8'))
                    threading.Thread(target=self.current_client_message_handler, args=(client_socket,)).start()
                else:
                    client_socket.send('-=-server-=-The main client is currently busy. Wait or try again later'.encode('utf-8'))
                    threading.Thread(target=self.waiting_client, args=(client_socket,)).start()
            else:
                client_socket.send("-=-server-=-Incorrect signature".encode('utf-8'))
        except socket.error:
            print(f"Socket error in client_check with socket {client_socket}")
        time.sleep(1)

    def main_message_handler(self, main_client_socket: socket.socket):
        print('main client connected')
        while True:
            try:
                if online_check(main_client_socket):
                    if online_check(self.client):
                        print(f'client {self.client} is omline')
                        self.main_client_available_status = False
                        data = self.client.recv(1024)
                        main_client_socket.send(data)
                    else:
                        print('client is now offline ')
                        self.main_client_available_status = True
                else:
                    break

                if online_check(main_client_socket):
                    if online_check(self.client):
                        self.main_client_available_status = False
                        data_send = main_client_socket.recv(1024)
                        self.client.send(data_send)
                    else:
                        print('client is now offline ')
                        self.main_client_available_status = True
                else:
                    break
            except socket.error:
                print(f"-=-server-=-Main client disconnected.  main {main_client_socket} and client {self.client}")
                self.main_client_available_status = False
                break
            time.sleep(1)

    def current_client_message_handler(self, client_socket: socket.socket):
        print("current client connected")
        while True:
            try:
                if online_check(client_socket):
                    if online_check(self.main_client):
                        data = client_socket.recv(1024)
                        self.main_client.send(data)

                    else:
                        client_socket.send("-=-server-=-Main client is offline. Retrying in 10 seconds".encode('utf-8'))
                        time.sleep(10)
                else:
                    print("Client is now offline")
                    break

                if online_check(client_socket):
                    if online_check(self.main_client):
                        data_send = self.main_client.recv(1024)
                        client_socket.send(data_send)
                    else:
                        client_socket.send("-=-server-=-Main client is offline. Retrying in 10 seconds".encode('utf-8'))
                        time.sleep(10)
                else:
                    print("Client is now offline")
                    break
            except socket.error:
                print(f"Current client disconnected. main {self.main_client} and client {client_socket}")
                self.main_client_available_status = True
                break
            time.sleep(1)

    def waiting_client(self, waiting_client_socket: socket.socket):
        print("waiting client connected")
        while True:
            try:
                if online_check(waiting_client_socket):
                    if online_check(self.main_client):
                        if self.main_client_available_status:
                            waiting_client_socket.send("=-server-=-You are connected to the main client".encode('utf-8'))
                            threading.Thread(target=self.current_client_message_handler, args=(waiting_client_socket,))
                        else:
                            time.sleep(10)
                            waiting_client_socket.send('-=-server-=-The main client is still busy. Retrying in 10 seconds'.encode('utf-8'))
                    else:
                        waiting_client_socket.send("-=-server-=-Main client is offline. Retrying in 10 seconds".encode('utf-8'))
                        time.sleep(10)
                else:
                    break
            except socket.error:
                print(f"Waiting client disconnected. main {self.main_client} and waiting client {waiting_client_socket}")
                break
            time.sleep(1)


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    print(ip)
    server = Server(ip, 5556)