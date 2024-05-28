import socket
import threading
import mysql.connector
HEADER = 64
PORT = 4300
FORMAT = 'utf-8'
DISCONNECT = 'disconnect'
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDR)
session = ""
def handle_private(username, recipient_username,message):
    global session
    full_message = f"private:{username}:{recipient_username}:{message}"
    try:
        msg = full_message
        
        message = msg.encode(FORMAT)
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        print("the message being sent is ",message)
        s.send(send_length)
        s.send(message)
    except OSError as e:
        print(f"Socket error: {e}")

    

def connect_database():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Lamloanhiepanh1996@",
            database="chat_app")
        if db.is_connected():
            return db
    except Error as e:
        print("error in query ",e)
        return None

def login(username,password):
    global session
    db = connect_database()
    print("logging in")
    if db:
        exe = db.cursor()
        print("exe worked")
        try:
            exe.execute("SELECT* FROM users WHERE username=%s AND pass_word =%s",(username,password))
            if(exe):
                user = exe.fetchone()
                if user:
                    print("logging successfully")
                    session = username
                    print("The current user is ",session)
                    send_user(session)
                    return True
                else:
                    print("wrong password")
                    return False
        finally:
            db.commit()
            db.close()
    else:
        return False
        print("not connected")


def register(username,pass_word):
    db = connect_database()
    if db:
        print("creating an account........")
        exe = db.cursor()
        try:
            exe.execute("INSERT INTO users (username,pass_word) VALUES (%s,%s)",(username,pass_word))
            print("account was registered")
        finally:
            db.commit()
            db.close()
    else:
        print("not connected")

def receive():
    listen = True
    while listen:
        try:
            message_length = s.recv(HEADER).decode(FORMAT)
            if message_length:
                try:
                    message_length = int(message_length)
                except ValueError:
                    print("Invalid message length:", message_length)
                    continue  # Skip processing this message

                print("Received message length:", message_length)

                try:
                    message = s.recv(message_length).decode(FORMAT)
                except ValueError as e:
                    print("Error decoding message:", e)
                    continue  # Skip processing this message

                if message == DISCONNECT:
                    listen = False
                    print("Server disconnected.")
                else:
                    print(f"Message received: {message}")
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
    global session
    while True:
        try:
            msg = input("Enter your message: ")
            if msg == DISCONNECT:
                s.send(DISCONNECT.encode(FORMAT))
                s.close()
                break
            elif msg.startswith('@:'):
                parts = msg.split(':', 2)
                recipient_username = parts[1]
                print("rep: ",recipient_username)
                message = parts[2]
                print("the message is: ",message)
                handle_private(session,recipient_username,message)
            else:
                #place
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
def send_user(username):

    try:
        msg = "user:"
        msg+=username
        message = msg.encode(FORMAT)
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        s.send(send_length)
        s.send(message)
    except OSError as e:
        print(f"Socket error: {e}")
        
    
       
receive_thread = threading.Thread(target=receive)
receive_thread.start()

decision = input("Login or Register: l for login, r for register ")
if(decision=='l' or decision=='L'):
    login_name =input("Enter your username ")
    password = input("Enter your password ")
    login(login_name,password)
elif decision=='R' or decision=='r':
    reg_name = input("Enter your username to register ")
    reg_password = input("enter your password to register ")
    register(reg_name,reg_password)
    decision = reg_name
if decision!="":
    send()
    
#client
    
  