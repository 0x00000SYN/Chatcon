#!/usr/bin/python3


from os import access
import socket
import threading
from time import sleep

host = input("Enter the HOST(Enter to use lo): ")
port = int(input("Enter PORT: "))

sock = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
sock.bind((host , port))
sock.listen(2)


connections = []

def share_keys():
    key1 = None
    key2 = None
    sock.settimeout(3)
    while True:
        connections[0].send(b"skp")
        key1 = connections[0].recv(1024)            
    
        connections[1].send(b"skp")
        key2 = connections[1].recv(1024)

        if key1 and key2:
            break
    
    sock.settimeout(None)
    connections[0].send(key2)
    connections[1].send(key1)



def listen_to_f_cli():                
    while True:
        msg1 = connections[0].recv(2048)
        connections[1].send(msg1)

def listen_to_s_cli():
    while True:
        msg2 = connections[1].recv(2048)
        connections[0].send(msg2)

def start_chat():
    t1 = threading.Thread(target=listen_to_f_cli)
    t2 = threading.Thread(target=listen_to_s_cli)
    
    t1.start()
    t2.start()

    t1.join()
    t2.join()

def accept():
    while True:
        conn , addr = sock.accept()
        connections.append(conn)

        if len(connections) < 2:
            accept()
        elif len(connections) == 2:
            share_keys()
            start_chat()

accept()
