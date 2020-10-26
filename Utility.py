#!/usr/bin/python3
def my_sendall(sock, data):
    if len(data) == 0:
        return None
    ret = sock.send(data)
    return my_sendall(sock, data[ret:])


def largest(array):
    n = len(array)
    max_elem = array[0]
    index = 0
    for i in range(1, n):
        if array[i] > max_elem:
            max_elem = array[i]
            index = i
    return index


def winning_state(array):
    for num in array:
        if num > 0:
            return False
    return True


def deep_clone(arr):
    clone = []
    for i, element in enumerate(arr):
        clone.append(element)
    return clone


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
