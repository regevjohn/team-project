import time
import socket
import errno
import sys
import pickle
import threading
import cv2

def send():
    # this complication is because two programs are trying to access the same camera together
    while True:
        video = cv2.VideoCapture(0)
        time.sleep(3)
        ret, frame = video.read()
        if frame.shape:
            message = pickle.dumps(frame)
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)
        video.release()
        time.sleep(3)
    # the real code should go as follows
    # video = cv2.VideoCapture(0)
    # while True:
    #     ret, frame = video.read()
    #     if frame.shape:
    #         message = pickle.dumps(frame)
    #         message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    #         client_socket.send(message_header + message)


def recieve():
    while True:
        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing username length, it's size is defined and constant
                username_header = client_socket.recv(HEADER_LENGTH)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(username_header):
                    print('Connection closed by the server')
                    while True:
                        pass
                    sys.exit()

                # Convert header to int value
                username_length = int(username_header.decode('utf-8').strip())

                # Receive and decode username
                username = client_socket.recv(username_length).decode('utf-8')

                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length)
                cv2.imshow(my_username, pickle.loads(message))
                cv2.waitKey(0)


        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                while True:
                    pass
                sys.exit()

            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            while True:
                pass
            sys.exit()



HEADER_LENGTH = 16

IP = "127.0.0.1"
PORT = 1234


my_username = input("Username: ")
my_ID = input("Press your ID (2-9 digits): ")

print(f'{my_username} > ', end= '')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((IP, PORT))

client_socket.setblocking(False)

mes = str(len(my_ID)) + my_ID + my_username
mes = mes.encode('utf-8')

#username = my_username.encode('utf-8')
username_header = f"{len(mes):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + mes)


t1 = threading.Thread(target=send)
t2 = threading.Thread(target=recieve)
t1.start()
t2.start()

