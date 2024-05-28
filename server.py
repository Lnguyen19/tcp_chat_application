import socket
import threading

HEADER = 64
PORT = 4300
FORMAT = 'utf-8'
DISCONNECT = 'disconnect'
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)
clients = []
usernames = []
lock = threading.Lock()

def send_private_message(sender_username, recipient_username, private_message):
    with lock:
        for user, conn in clients:
            if user == recipient_username:
                try:
                    message = f"Private message from {sender_username}: {private_message}".encode(FORMAT)
                    message_length = len(message)
                    send_length = str(message_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    conn.send(send_length)
                    conn.send(message)
                except OSError as e:
                    print(f"Socket error: {e}")
                break  

def online():
    with lock:
        user_list = ', '.join(user for user, _ in clients)
        message = f"Online users: {user_list}".encode(FORMAT)
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        for _, conn in clients:
            try:
                conn.send(send_length)
                conn.send(message)
            except Exception as e:
                print("Error sending online users:", e)
                conn.close()
                clients.remove((user, conn))

def broadcast(message, client):
    with lock:
        for _, conn in clients:
            if conn != client:
                try:
                    conn.send(message)
                except:
                    clients.remove((user, conn))

def handle_client(conn, addr):
    print("New connection", addr)
    connected = True
    username = None
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg.startswith('user:'):
                    username = msg.split(':', 1)[1]
                    if username:
                        with lock:
                            clients.append((username, conn))
                        print(addr, ":", msg)
                        online()
                elif msg.startswith('private:'):
                    parts = msg.split(':', 3)
                    sender_username = parts[1]
                    recipient_username = parts[2]
                    private_message = parts[3]
                    send_private_message(sender_username, recipient_username, private_message)
                else:
                    broadcast(f"[{username}] {msg}".encode(FORMAT), conn)
                if msg == DISCONNECT:
                    connected = False
        except:
            connected = False

    with lock:
        for client_tuple in clients:
            if client_tuple[1] == conn:
                clients.remove(client_tuple)
                username = client_tuple[0]
                if username in usernames:
                    usernames.remove(username)
                online()
                break
    conn.close()

def main():
    server_socket.listen()
    print("Server is starting...")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("Active connections:", threading.active_count() - 1)

main()
