#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, socket, struct, random, string


def hexgen(length):
    hex = "".join([random.choice(string.hexdigits) for x in range(length)])
    return hex


def encrypt(plaintext, key):
    return bytearray(
        [plaintext[i] ^ key[i]
         for i in range(len(plaintext))
         ])


def decrypt(ciphertext, key):
    return bytearray(
        [ciphertext[i] ^ key[i]
         for i in range(len(ciphertext))
         ])


def send_and_receive_tcp(address, tcpport, clientkeylist):
    tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    keylist = "\r\n".join(clientkeylist)
    tcpsocket.connect((address, tcpport))
    tcpsocket.send("HELLO ENC\r\n"+keylist+"\r\n"+".\r\n")
    data = tcpsocket.recv(2048)
    return data


def send_and_receive_udp(address, udpport, cid, clientkeylist, serverkeylist):
    udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    clientkeylist.reverse()
    serverkeylist.reverse()
    udpport = int(udpport)
    cid = str(cid)

    init_msg = "Hello from "+cid
    msg = " "
    init_length = len(init_msg)
    length = 0
    ack = True
    eom = False
    data_remaining = 0    
    
    plaintext = bytearray(init_msg, 'utf-8')
    key = clientkeylist.pop()
    key = bytearray(key, 'utf-8')
    init_msg = encrypt(plaintext, key)
    init_msg = str(init_msg)

    sent_msg = struct.pack('!8s??HH64s', cid, ack, eom, data_remaining, init_length, init_msg)

    udpsocket.sendto(sent_msg, (address, udpport))

    while 1:
        recv_msg, addr = udpsocket.recvfrom(2048)

        cid, ack, eom, data_remaining, length, msg = struct.unpack('!8s??HH64s', recv_msg)
        msg = msg[:length]
        
        if eom == 0:
            ciphertext = bytearray(msg, "utf-8")
            key = serverkeylist.pop()
            key = bytearray(key, 'utf-8')
            msg = decrypt(ciphertext, key)
            msg = str(msg)
            print("Received message: "+msg)

            temp = msg.split()
            temp.reverse()
            msg = " ".join(temp)
            length = len(msg)
            print("Sent message: "+msg)

            plaintext = bytearray(msg, 'utf-8')
            key = clientkeylist.pop()
            key = bytearray(key, 'utf-8')
            msg = encrypt(plaintext, key)
            msg = str(msg)

            sent_msg = struct.pack('!8s??HH64s', cid, ack, eom, data_remaining, length, msg)

            udpsocket.sendto(sent_msg, (address, udpport))

        else:
            cid, ack, eom, data_remaining, length, msg = struct.unpack('!8s??HH64s', recv_msg)
            msg = msg[:length]
            print("Received message: "+msg)
            udpsocket.close()
            break

    return


# MAIN
address = str(sys.argv[1])
tcpport = int(sys.argv[2])

clientkeylist = []

for i in range(0, 20):
    key = hexgen(64)
    clientkeylist.append(key)

tcpdata = send_and_receive_tcp(address, tcpport, clientkeylist)
msg, cid, udp = tcpdata.split(" ", 3)
serverkeylist = udp.split("\r\n")
udpport = serverkeylist.pop(0) #remove udpport no. from beginning of list and add to udpport var
serverkeylist.pop() # remove . and other stuff from end of list
serverkeylist.pop()

send_and_receive_udp(address, udpport, cid, clientkeylist, serverkeylist)
