# !/usr/bin/env python3

import socket
import struct
import sys
import Utility

PORT = 6444
SERVER_ADDRESS = socket.gethostname()

SEND_PACKED_FORMAT = '>ii'
RECEIVE_PACKED_FORMAT = '>iiii'
"""
status = heaps[3]
options:
0 - continue game regularily
1 - client Win
-1 - client lose + leagal move
-2 - client lose + illegal move
-3 - improper move
"""


def recv_data(dest_socket, length):
    data = b''
    remaining_length = length
    while remaining_length:
        current_data = dest_socket.recv(remaining_length)
        if not current_data:
            if data:
                raise Exception('Server returned corrupted data')
            else:
                return data
        data += current_data
        remaining_length -= len(current_data)
    return data


def status_handle(heaps, is_first_round):
    status = heaps[3]
    if is_first_round:
        print('Heap A: %d\n' % (heaps[0]))
        print('Heap B: %d\n' % (heaps[1]))
        print('Heap C: %d\n' % (heaps[2]))
        print('Your turn')

    elif status == 0:
        print('Move accepted')
        print('Heap A: %d\n' % (heaps[0]))
        print('Heap B: %d\n' % (heaps[1]))
        print('Heap C: %d\n' % (heaps[2]))
        print('Your turn')
    elif status == 1:
        print('Move accepted')
        print('Heap A: %d\n' % (heaps[0]))
        print('Heap B: %d\n' % (heaps[1]))
        print('Heap C: %d\n' % (heaps[2]))
        print('You win!')
    elif status == -1:
        print('Move accepted')
        print('Heap A: %d\n' % (heaps[0]))
        print('Heap B: %d\n' % (heaps[1]))
        print('Heap C: %d\n' % (heaps[2]))
        print('You lose!')
    elif status == -2:
        print('Illegal move')
        print('Heap A: %d\n' % (heaps[0]))
        print('Heap B: %d\n' % (heaps[1]))
        print('Heap C: %d\n' % (heaps[2]))
        print('Server win!')
    else:
        print('Illegal move')
        print('Heap A: %d\n' % (heaps[0]))
        print('Heap B: %d\n' % (heaps[1]))
        print('Heap C: %d\n' % (heaps[2]))
        print('Your turn')


def request_game_state(server_address, server_port, is_first_round):
    end_game = False
    with socket.socket() as server_socket:
        server_socket.connect((server_address, server_port,))
        packed_data = recv_data(server_socket, 16)
        unpacked_data = struct.unpack(RECEIVE_PACKED_FORMAT, packed_data)
        heaps = [int(unpacked_data[0]), int(unpacked_data[1]), int(unpacked_data[2]), int(unpacked_data[3])]
        status_handle(heaps, is_first_round)
        if heaps[3] == 0 or heaps[3] == -3:
            #heap, amount = input("Enter a two value: ").split()
            #heap = list(map(str, input("Enter move: ").split()))
            user_input = list(input("Enter move: ").split())
            if user_input[0] == 'Q':
                end_game = True
            else:
                heap = ord(user_input[0]) - ord('A')
                # heap = chr(heap)
                amount = int(user_input[1])
                packed_data_to_send = struct.pack(SEND_PACKED_FORMAT, heap, amount)
                Utility.my_sendall(server_socket, packed_data_to_send)
        else:
            end_game = True
        server_socket.shutdown(socket.SHUT_RDWR)
    return end_game


def main(server_address, server_port):
    print('nim')
    end_game = False
    is_first_round = True
    while not end_game:
        end_game = request_game_state(server_address, server_port, is_first_round)
        is_first_round = False
        # heap, amount = input("Enter a two value: ").split()
        # amount = int(amount)



if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 1 or argc > 3:
        print("argument error")
        sys.exit()
    # tuple (address, port)
    # argv variables are string and server port is int. Conversion needed
    Server_address = sys.argv[1] if argc == 2 else SERVER_ADDRESS
    Server_port = int(sys.argv[2]) if argc == 3 else PORT
    main(Server_address, Server_port)
