#!/usr/bin/python3
import socket
import sys
import struct
import copy

SERVER_SEND_FORMAT = '>iiiiiii'
SERVER_REC_FORMAT = '>iiii'
PAD = -3
START = -1
END = -2
max_bandwidth = 10000
EOF_LIKE = b''
buff_log = 5
BAD_INPUT = -100


def my_sendall(sock, data):
    if len(data) == 0:
        return None
    ret = sock.send(data)
    return my_sendall(sock, data[ret:])


def send_heaps(socket, heaps, accepted, win):
    send_msg = [START, accepted, heaps[0], heaps[1], heaps[2], win, END]

    send_msg = [int(e) for e in send_msg]
    try:
        my_sendall(socket,
                   struct.pack(SERVER_SEND_FORMAT, send_msg[0], send_msg[1], send_msg[2], send_msg[3], send_msg[4],
                               send_msg[5], send_msg[6]))
    except socket.error as exc:
        print("An error occurred: %s\n" % exc)
        sys.exit()


def fill_buff(sock):  # also: return 1 if connection is terminated, and 0 otherwise.\
    buff = ()
    try:
        raw_data = sock.recv(max_bandwidth)
    except socket.error as exc:
        print("An error occurred: %s\n" % exc)
        sys.exit()

    if raw_data == EOF_LIKE:
        sock.close()
        return 1, buff
    buff = struct.unpack(SERVER_REC_FORMAT, raw_data)
    while not (buff[0] == START and buff[-1] == END):
        try:
            raw_data = sock.recv(max_bandwidth)
        except socket.error as exc:
            print("An error occurred: %s\n" % exc)
            sys.exit()
        if raw_data == EOF_LIKE:
            sock.close()
            return 1, buff
        buff += struct.unpack(SERVER_REC_FORMAT, sock.recv(max_bandwidth))
    return 0, buff


def server_move(heaps):
    new_heaps = heaps
    if heaps[0] >= heaps[1]:
        if heaps[0] >= heaps[2]:
            new_heaps[0] -= 1
        else:
            new_heaps[2] -= 1
    else:
        if heaps[1] >= heaps[2]:
            new_heaps[1] -= 1
        else:
            new_heaps[2] -= 1
    return new_heaps


def main(port, heaps):
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind(('', port))
    listening_socket.listen(buff_log)
    while True:
        print('Server: listening %s:%s' % ('localhost', port,))
        client_socket, address = listening_socket.accept()
        print('Connection from %s : %s has been established!' % (address, port))
        local_heaps = copy.deepcopy(heaps)
        send_heaps(client_socket, local_heaps, PAD, 2)
        while True:
            termination, buff = fill_buff(client_socket)
            if termination:
                client_socket.close()
                break
            if int(buff[1]) == BAD_INPUT:
                local_heaps = server_move(local_heaps)
                if local_heaps == [0, 0, 0]:
                    send_heaps(client_socket, local_heaps, 0, 0)
                else:
                    send_heaps(client_socket, local_heaps, 0, 2)
            elif int(buff[2]) > int(local_heaps[int(buff[1])]):
                local_heaps = server_move(local_heaps)
                if local_heaps == [0, 0, 0]:
                    send_heaps(client_socket, local_heaps, 0, 0)
                else:
                    send_heaps(client_socket, local_heaps, 0, 2)
            else:
                local_heaps[int(buff[1])] -= int(buff[2])
                if local_heaps == [0, 0, 0]:
                    send_heaps(client_socket, local_heaps, 1, 1)
                else:
                    local_heaps = server_move(local_heaps)
                if local_heaps == [0, 0, 0]:
                    send_heaps(client_socket, local_heaps, 1, 0)
                else:
                    send_heaps(client_socket, local_heaps, 1, 2)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("[ERROR] Heaps size should be supplied ")
        sys.exit()
    na, nb, nc = sys.argv[1], sys.argv[2], sys.argv[3]
    heaps = [int(na), int(nb), int(nc)]
    port = 6444 if (len(sys.argv) < 5) else sys.argv[4]
    port = int(port)
    main(port, heaps)
