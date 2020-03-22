import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = []
            while True:
                try:
                    conn.settimeout(0.2)
                    packet = conn.recv(4096)
                    if not packet:
                        break
                    data.append(packet)
                except socket.timeout:
                    break
            if not data:
                continue
            conn.sendall(b''.join(data))
