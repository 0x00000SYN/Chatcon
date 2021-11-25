#!/usr/bin/python3

from curses import *
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from time import sleep
import base64
import os
import socket
import threading
from shutil import rmtree

from Crypto.PublicKey.pubkey import pubkey

stdscr = initscr()

host = ""
port = None
name = None

stop_threads = False

def main(stdscr):
    banner = """ 
                    ▄▄                                                    
          ▄▄█▀▀▀█▄  ██                 ██    ▄▄█▀▀▀█▄█                    
        ▄██▀     ▀█ ██                 ██  ▄██▀     ▀█                    
        ██▀       ▀ ███████▄  ▄█▀██▄ ████████▀       ▀  ▄██▀██▄▀████████▄  
        ██          ██    ██ ██   ██   ██  ██          ██▀   ▀██ ██    ██  
        ██▄         ██    ██  ▄█████   ██  ██▄         ██     ██ ██    ██  
        ▀██▄     ▄▀ ██    ██ ██   ██   ██  ▀██▄     ▄▀ ██▄   ▄██ ██    ██  
         ▀▀█████▀█  ██  ████▄████▀██▄ ▀████ ▀▀█████▀   ▀█████▀▄████  ████▄

            BY :> 0x5YN                                                 
    """

    h , w = os.popen("stty size" , "r").read().split()
    con_h = int(h)
    con_w = int(w)
    global mwin , bwin , YELLOW , RED , GREEN , BOLD
    mwin = newwin(con_h - 1 , con_w , 0 , 0)
    bwin = newwin(1 , con_w , con_h - 1 , 0)
    bwin.erase()
    mwin.erase()
    echo()

    initscr()
    use_default_colors()

    init_pair(1 , COLOR_RED , -1)
    init_pair(2 , COLOR_GREEN , -1)
    init_pair(3 , COLOR_YELLOW , -1)
    RED = color_pair(1)
    GREEN = color_pair(2)
    YELLOW = color_pair(3)

    mwin.addstr(banner , YELLOW)
    mwin.addstr("\n\r")
    get_info()
        





def get_info():
    bwin.addstr(": ")
    ref()
    sleep(0.5)
    help()
    ref()
    global host , port , name


    while True:
        c = bwin.getstr()
        cmd = c.decode("ascii").split(" ")
        if (cmd[0]) == "/connect":
            try:
                host = cmd[1]
                port = cmd[2]
                try:
                    mwin.addstr("SERVER HOST: {}:{}\n".format(host , port))
                except:
                    mwin.erase() 
                    mwin.addstr("SERVER HOST: {}:{}\n".format(host , port))
            except:
                try:
                    mwin.addstr("Somthing wrong!\n" , RED|A_BOLD)
                except:
                    mwin.erase() 
                    mwin.addstr("Somthing wrong!\n" , RED|A_BOLD)
                
        elif cmd[0] == "/name":
            try:
                uname = cmd[1]
                mwin.addstr("USERNAME: {}\n".format(uname))
                name = uname
            except:
                mwin.addstr("Somthing wrong!\n" , RED|A_BOLD)
        elif cmd[0] == "/join":
            if host == "" and name == None and port == None:
                mwin.addstr("Be sure you defined a host and name\n" , RED|A_BOLD)    
            else:
                create_socket(str(host) , int(port))
                break
        elif cmd[0] == "/exit":
            exit()
        else:
            try:
                help()
            except:
                mwin.erase() 
                help()

        ref()
        bref()


def ref():
    mwin.refresh()
    bwin.refresh()
def bref():
    bwin.erase()
    bwin.addstr(": ")
def help():
    mwin.addstr("USAGE:\n\t/connect\t: use /connect SERVER_IP PORT.\n")
    mwin.addstr("\t/name\t\t: use /name USER_NAME to set nickname to.\n")
    mwin.addstr("\t/join\t\t: use /join to enter the room\n")
   # mwin.addstr("\t/help\t\t: to show this page.\n")
    mwin.addstr("\t/exit\t\t: quit the program.\n")



#----------------------socket---------------------------
def create_socket(host , port):
    global sock
    sock = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    sock.connect((host , port))
    generate_keys()
    share_keys()
    start_chat()

def share_keys():
    mwin.addstr("***Wait for other Peer to be connected\n")
    mwin.addstr("[+] Share keys: ")
    ref()
    bref()
    
    cmd = sock.recv(1024)
    if cmd.decode() == "skp":
    
        path = os.path.join(os.path.expanduser("~") , ".chatcon")
        pkp = os.path.join(path , "pub.key")
        fk = open(pkp , "rb")
        key = fk.read()
        sock.send(key)
        fk.close()

        other_key = sock.recv(1024)

        okfile = os.path.join(path , "other_key.key")
        okeyfile = open(okfile , "wb")
        okeyfile.write(other_key)
        okeyfile.close()

        mwin.addstr("Done!\n" , GREEN|A_BOLD)
        ref()
        bref()


def listen_to_messages():
    while True:
        if stop_threads == True:
            break
        else:
            msg = sock.recv(2048)
            if msg.decode().find(">>>") == 0:
                mwin.addstr(msg , GREEN|A_BOLD)
            
            elif msg.decode().find("<<<") == 0:
                mwin.addstr(msg , RED|A_BOLD)
            
            else:
                try:
                    dm = decrypt(msg.decode())
                    mwin.addstr(dm , YELLOW)
                except:
                    mwin.addstr("[x] Somthing Wrong with Decryption! Please Try Again\n" , RED|A_BOLD)
            ref()
            bref()
    exit()

def send_messages():
    global stop_threads
    while True:
        if stop_threads == True:
            break
        else:
            msg = bwin.getstr()
            if msg.decode() == "/exit":
                msg = "<<< " + name + " exit!\n"
                sock.send(msg.encode())
                stop_chat()
            elif msg.decode() == "/clear":
                mwin.erase()
                ref()
                bref()
            elif msg.decode() == "/help":
                mwin.addstr("/clear\t: Clear screen\n/help\t: Show this help\n/exit\t: Exit the chat")
                ref()
                bref()
            else:
                fmsg = name + ": " + msg.decode() + "\n"
                mwin.addstr("you: " + msg.decode() + "\n")
                sock.send(encrypt(fmsg))
            ref()
            bref()
    exit()

def start_chat():
    mwin.erase()
    ref()
    bref()
    global t1, t2
    t1 = threading.Thread(target=listen_to_messages)
    
    msg = ">>> " + name + " joined!\n"
    sock.send(msg.encode())

    t2 = threading.Thread(target=send_messages)

    t1.start()
    t2.start()

    t1.join()
    t2.join()



def stop_chat():
    global stop_threads , t1 , t2
    mwin.erase()
    ref()
    bref()
    clear_keys()
    endwin()
    sock.close()
    os._exit(0)
#----------------------encryption----------------------
def generate_keys():
    mwin.erase()
    mwin.addstr("[+] Generate Keys: ")
    ref()
    bref()
    sleep(0.2)
    try:
        home = os.path.expanduser("~")
        path = os.path.join(home , ".chatcon")
        os.mkdir(path)
    except:
        pass
    
    key_pair = RSA.generate(2048)

    private = key_pair.exportKey()
    public = key_pair.publickey().exportKey() 

    kf = open(os.path.join(path , "pri.key") , "wb")
    kf.write(private)
    kf.close()

    kf = open(os.path.join(path , "pub.key") , "wb")
    kf.write(public)
    kf.close()

    mwin.addstr("Done!\n" , GREEN|A_BOLD)
    ref()
    bref()

def encrypt(msg):
    path = os.path.join(os.path.expanduser("~") , ".chatcon/other_key.key")
    f = open(path , "r")
    pk = RSA.importKey(f.read())
    pkey = PKCS1_OAEP.new(pk)
    emsg = pkey.encrypt(msg.encode())
    fmsg = base64.b64encode(emsg)
    return fmsg

def decrypt(msg):
    path = os.path.join(os.path.expanduser("~") , ".chatcon/pri.key")
    f = open(path , "r")
    pk = RSA.importKey(f.read())
    prikey = PKCS1_OAEP.new(pk)
    dmsg = base64.b64decode(msg)
    fmsg = prikey.decrypt(dmsg) 
    return fmsg



def clear_keys():
    mwin.addstr("[*] Clear Keys: ")
    ref()
    bref()
    try:
        path = os.path.join(os.path.expanduser("~") , ".chatcon")
        rmtree(path)
    except:
        mwin.addstr("Fail!\n" , RED|A_BOLD)
        sleep(0.5)
    mwin.addstr("Done!\n" , GREEN|A_BOLD)
    ref()
    bref()


wrapper(main)

