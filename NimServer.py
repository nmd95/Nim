#!/usr/bin/env python3
import socket
import struct
import sys
import Utility

# Seeking the whole memory
ROOT_PATH = '/'
# Arbitrary port number
PORT = 6444
# > = big-endian , c - char, i - int
SEND_PACKED_FORMAT = '>iiii'
RECEIVE_PACKED_FORMAT = '>ii'
# Arbitrary buffer length - should be sufficient
BUFFER_LENGTH = 1024

"""
status = heaps[3]
options:
0 - continue game regularily
1 - client Win
-1 - client lose + leagal move
-2 - client lose + illegal move
-3 - improper move
"""


def server_turn(heaps, client_heap, clientAmount):
    # checking for illegal move of client
    if client_heap == -1 or (heaps[client_heap] - clientAmount) < 0 or clientAmount <= 0:
        index = Utility.largest(heaps)
        heaps[index] -= 1
        if Utility.winning_state(heaps):
            # client lose
            heaps[3] = -2
            return heaps
        else:
            heaps[3] = -3
            return heaps
    # client legal move
    else:
        heaps[client_heap] -= clientAmount
        if Utility.winning_state(heaps):
            # client win
            heaps[3] = 1
            return heaps
        else:
            # continue game
            index = Utility.largest(heaps)
            heaps[index] -= 1
            if Utility.winning_state(heaps):
                # client lose + legal move though
                heaps[3] = -1
                return heaps
            else:
                heaps[3] = 0
                return heaps


def send_packed_heaps(client_sock, heaps):
    packed_data = struct.pack(SEND_PACKED_FORMAT, heaps[0], heaps[1], heaps[2], heaps[3])
    Utility.my_sendall(client_sock, packed_data)
    game_over = True if (heaps[3] == -2 or heaps[3] == -1 or heaps[3] == 1) else False
    return game_over


def extract_client_input(client_packed_data):
    client_input = struct.unpack(RECEIVE_PACKED_FORMAT, client_packed_data)
    client_heap = int(client_input[0])
    if client_heap < 0 or client_heap > 2:
        client_heap = -1
    client_amount = int(client_input[1])
    return client_heap, client_amount


def handle_client(client_socket, heaps):
    send_packed_heaps(client_socket, heaps)
    client_packed_data = Utility.recv_data(client_socket, 8)
    # client_packed_data = client_socket.recv(BUFFER_LENGTH)
    # client_packed_data = client_socket.recv(8)
    client_heap, client_amount = extract_client_input(client_packed_data)
    heaps = server_turn(heaps, client_heap, client_amount)
    game_over = send_packed_heaps(client_socket, heaps)
    return game_over


def main(SERVER_PORT, heaps):
    heap_clone = Utility.deep_clone(heaps)
    # heaps_clone = heaps
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ListeningSocket:
        # server_address = ('localhost', SERVER_PORT)
        print(socket.gethostbyname(socket.gethostname()))
        server_address = (socket.gethostname(), SERVER_PORT)
        print('starting up on %s port %s' % server_address)
        ListeningSocket.bind(server_address)
        ListeningSocket.listen(1)

        while True:
            game_over = False
            while not game_over:
                try:
                    print('Server: listening %s:%s' % ('localhost', SERVER_PORT,))
                    client_socket, client_address = ListeningSocket.accept()
                    with client_socket:
                        print('Server: client %s connected' % (client_address,))
                        game_over = handle_client(client_socket, heap_clone)
                        client_socket.shutdown()
                    if game_over:
                        heap_clone = Utility.deep_clone(heaps)
                except Exception as e:
                    print('Client error: %s' % (e,))
                    continue
if __name__ == '__main__':
    argc = len(sys.argv)
    arr = []
    if argc < 3 or argc > 4:
        print("argument error")
        sys.exit()
    Server_port = sys.argv[1] if argc == 5 else PORT
    arr.append(int(sys.argv[1]) if argc == 4 else int(sys.argv[2]))
    arr.append(int(sys.argv[2]) if argc == 4 else int(sys.argv[3]))
    arr.append(int(sys.argv[3]) if argc == 4 else int(sys.argv[4]))
    arr.append(0)
    main(Server_port, arr)
