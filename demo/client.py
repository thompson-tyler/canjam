#
#   CLIENT.PY
#   Skylar's silly stupid tester client
#

import socket

# me
LOCAL_HOST = "10.243.43.94"
# LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 1024

# them
REMOTE_HOST = "10.243.62.217"
REMOTE_PORT = 1025

TIMEOUT = 1.0
TOTAL_NUM = 1000

# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Assign IP address and port number to socket
# serverSocket.settimeout(TIMEOUT)
serverSocket.bind((LOCAL_HOST, LOCAL_PORT))

seqNum = 0

while seqNum < TOTAL_NUM:
    # send message to server
    sendMsg = bytes("PING " + str(seqNum) + "\n", "utf-8")
    serverSocket.sendto(sendMsg, (REMOTE_HOST, REMOTE_PORT))
    seqNum += 1

    # janky
    receiveMsg = ""
    while not receiveMsg:
        try:
            receiveMsg, addr = serverSocket.recvfrom(REMOTE_PORT)
        except socket.timeout as e:
            break

    if receiveMsg:
        print(receiveMsg)
