import socket
import threading

HEADER = 64
PORT = 4300
FORMAT = 'utf-8'
DISCONNECT = 'disconnect'
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDR)

def receive():
    listen = True
    while listen:
        try:
            message_length = s.recv(HEADER).decode(FORMAT)
            if message_length:
                message_length = int(message_length)
                message = s.recv(message_length).decode(FORMAT)
                if message == DISCONNECT:
                    listen = False
                    print("Server disconnected.")
                else:
                    print(f"message: {message}")
        except ConnectionAbortedError:
            print("Connection aborted by host.")
            listen = False
        except ConnectionResetError:
            print("Connection reset by host.")
            listen = False
        except OSError as e:
            print(f"Socket error: {e}")
            listen = False
        finally:
            if not listen:
                s.close()

def send():
    while True:
        try:
            msg = input("Enter your message: ")
            if msg == DISCONNECT:
                s.send(DISCONNECT.encode(FORMAT))
                s.close()
                break
            message = msg.encode(FORMAT)
            message_length = len(message)
            send_length = str(message_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            s.send(send_length)
            s.send(message)
        except OSError as e:
            print(f"Socket error: {e}")
            s.close()
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

send()
