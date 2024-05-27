import socket
import threading
HEADER = 64
host = ""
PORT = 4300
FORMAT = 'utf-8'
DISCONNECT = 'disconnect'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', PORT))
clients = []
def broadcast(message,client):
	for client_ in  clients:
		if(client_==client):
			pass
		else:
			try :
				client_.send(message)
			except:
				 clients.remove(client_)


def handle_client(conn, addr):
    print("new connection", addr)
    #clients.append(conn)
    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                print(addr, ":", msg)
                if msg == DISCONNECT:
                    connected = False
                else:
                    broadcast(f"[{addr}] {msg}".encode(FORMAT), conn)
        except:
            connected = False
    conn.close()
    clients.remove(conn)








def main():
    server_socket.listen()
    print(server_socket)
    print("server is starting")
    value = True
    while(value):
        conn,addr = server_socket.accept()
        clients.append(conn)
        thread = threading.Thread(target = handle_client,args = (conn,addr))
        thread.start()
        print("active connections ",threading.active_count()-1)




main()
