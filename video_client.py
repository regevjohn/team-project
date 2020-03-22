import socket
import pickle
import cv2

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
video = cv2.VideoCapture(0)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    while True:
        ret, frame = video.read()
        # print(sys.getsizeof(frame))
        s.sendall(pickle.dumps(frame))

        data = []
        while True:
            try:
                s.settimeout(0.2)
                packet = s.recv(4096)
                if not packet:
                    break
                data.append(packet)
            except socket.timeout:
                break

        if data:
            cv2.imshow('image', pickle.loads(b''.join(data)))
            cv2.waitKey(1)
