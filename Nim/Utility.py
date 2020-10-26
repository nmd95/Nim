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

