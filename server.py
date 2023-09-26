import socket 
from threading import Thread


HEADER_LEN = 10
IP = "0.0.0.0"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
print(f"[SERVER STARTED on Port {PORT}]")

socket_list = [server_socket]
clients = []

def build_client(name, conn, addr):
    return {'name':name, 'socket':conn, 'addr':addr}

def read_header(conn):
    header = conn.recv(HEADER_LEN)
    if len(header) > 0:
        return int(header)
    else:
        return -1

def format_msg(msg):
    return bytes(f"{len(msg):<{HEADER_LEN}}" + msg, 'utf-8')

def forward(cur_client, msg):
    for client in clients:
        if client != cur_client:
            try:
                client['socket'].send(msg['header'] + msg['data'])
            except Exception as e:
                #clients.remove(client)
                print(e)
                print(f"FAILED TO FORWARD {msg}")
    

def rec_msg(client_socket):
    try:
        msg_header = client_socket.recv(HEADER_LEN)
        if len(msg_header) == 0 or int(msg_header) == -1:
            return False
        
        msg_len = int(msg_header.decode('utf-8').strip())
        return {"header":msg_header, "data":client_socket.recv(msg_len)}

    except:
        return False

def rec_user(conn, addr):
    msg_len = read_header(conn)

    data = conn.recv(msg_len)
    name = data.decode('utf-8')

    return name

def client_thread(client):
    client['socket'].send(format_msg("Welcome to the chat!"))

    while True:
        try:
            # Recieve message
            msg = rec_msg(client['socket'])
            if msg:
                # print(msg)
                # Broadcast message
                forward(client,msg)
            else:
                clients.remove(client)
                msg = f"{client['name']} has left . . ."
                print(msg)
                forward(client, {'header': bytes(f"{len(msg):<{HEADER_LEN}}",'utf-8'), 'data':bytes(msg,'utf-8')})

        except:
            pass


def accept():
    while True:
        conn, addr = server_socket.accept()
        # Accept new connection
        if conn:
            uname = rec_user(conn, addr)
            print(f"{uname} connected...")

            # Forward connection info to clients
            if len(clients) > 0:
                for client in clients:
                    try:
                        client['socket'].send(format_msg(f"{uname} has connected . . . "))
                        conn.send(format_msg(f"{client['name']} is connected"))
                    except:
                        #print(f"{client['name']} has left")
                        #clients.remove(client)
                        print("ERROR SENDING DATA TO CLIENT")


            client = build_client(uname, conn, addr)
            clients.append(client)

            t = Thread(target=client_thread, args=(client,))
            t.start()
                        
             
       
accept()

