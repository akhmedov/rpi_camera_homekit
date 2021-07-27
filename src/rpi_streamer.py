# https://picamera.readthedocs.io/en/latest/recipes1.html#streaming-capture

import socket
import picamera
import threading

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
splitter_port_busy = {1: False, 2: False, 3: False, 4: False}

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(4)


def action_on_connection(client, addr, splitter_port):
    connection = client.makefile('wb')
    try:
        camera.start_recording(connection, format='h264', splitter_port=splitter_port)
        camera.wait_recording(9999999, splitter_port=splitter_port)  # TODO: investigate infinite stream
    finally:
        splitter_port_busy[splitter_port] = False  # TODO: possible rase condition here
        camera.stop_recording(splitter_port=splitter_port)
        try:
            connection.close()
        finally:
            print('[WW] Connection closed by peer:', addr)


while True:
    client, addr = server_socket.accept()
    print('[II] Accepted connection from', addr)
    print('[II] Splitter ports befor connection:', splitter_port_busy)

    iter = 1
    while iter < 6:
        if iter == 5:
            print('[WW] All camera splitting ports are busy. Skipping connection...')
        if not splitter_port_busy[iter]:
            print(iter)
            splitter_port_busy[iter] = True
            threading.Thread(target=action_on_connection, args=(client, addr, iter)).start()
            break
        iter += 1

    print('[II] Splitter ports after connection:', splitter_port_busy)

# server_socket.close()
