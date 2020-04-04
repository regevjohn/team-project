import socket
import select

HEADER_LENGTH = 16

IP = "127.0.0.1"
PORT = 1234
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
clients = {}
ID_chats = {}

print(f'Listening for connections on {IP}:{PORT}...')


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        print()
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False

def div_mes(message):
    len_ID = int(message[0])
    ID = message[1:len_ID + 1]
    user_name = message[len_ID + 1:]
    return ID, user_name



while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            #It must be an ID + User name message
            user = receive_message(client_socket)
            if user is False:
                continue
            ID, user_name = div_mes(user['data'].decode())
            user_header = f"{len(user_name):<{HEADER_LENGTH}}".encode('utf-8')
            user = {'header': user_header, 'data': user_name.encode()}
            try:
                ID_chats[ID].append(client_socket)
            except KeyError:
                ID_chats[ID] = [client_socket]
            sockets_list.append(client_socket)
            clients[client_socket] = {'user': user, 'ID': ID}

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user_name)) #.decode('utf-8')
        else:
            message = receive_message(notified_socket)
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['user']['data'].decode('utf-8')))
                del clients[notified_socket]

                continue

            user = clients[notified_socket]['user']
            user_name = user['data']

            for client_socket in ID_chats[clients[notified_socket]['ID']]:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)

        del ID_chats[clients[notified_socket]['ID']][notified_socket]
        del clients[notified_socket]
