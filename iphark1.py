#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, socket, struct
from os import urandom


def keygen(length):
    return bytearray(urandom(length))


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


def send_and_receive_tcp(address, tcpport):
    tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    tcpsocket.connect((address, tcpport))
    tcpsocket.send("HELLO\r\n")
    data = tcpsocket.recv(1024)
    return data


def send_and_receive_udp(address, udpport, cid):
    udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udpport = int(udpport)

    init_msg = "Hello from " + cid
    msg = " "
    init_length = len(init_msg)
    length = 0
    ack = True
    eom = False
    data_remaining = 0
    
    plaintext = bytearray(msg)
    key = keygen(len(plaintext))
    print 'Before encrypting: ' + plaintext
    ciphertext = encrypt(plaintext, key)
    print 'After encrypting: ' + ciphertext

    
    sent_msg = struct.pack('!8s??HH64s', cid, ack, eom, data_remaining, init_length, init_msg)

    udpsocket.sendto(sent_msg, (address, udpport))

    while 1:
        recv_msg = udpsocket.recvfrom(1024)

        cid, ack, eom, data_remaining, length, msg = struct.unpack('!8s??HH64s', recv_msg)
        plaintext2 = decrypt(ciphertext, key)
        print 'After decrypting: ' + plaintext2
        print(msg)

        temp = msg.split()
        temp.reverse()
        msg = " ".join(temp)
        length = len(msg)

        sent_msg = struct.pack('!8s??HH64s', cid, ack, eom, data_remaining, length, msg)

        udpsocket.sendto(sent_msg, (address, udpport))


        if eom == 1:
            break
        udpsocket.close()

    return


# MAIN
address = str(sys.argv[1])
tcpport = int(sys.argv[2])

tcpdata = send_and_receive_tcp(address, tcpport)
msg, cid, udpport = tcpdata.split(" ")

send_and_receive_udp(address, udpport, cid)
