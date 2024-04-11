#
#   SERVER.PY
#   Skylar's silly stupid tester server
#

import socket

# me
LOCAL_HOST = "10.243.62.217"
LOCAL_PORT = 1025

# them
REMOTE_HOST = "10.243.43.94"
REMOTE_PORT = 1024

TIMEOUT = 1.0
TOTAL_NUM = 10

# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket.sockets
# Assign IP address and port number to socket
# serverSocket.settimeout(TIMEOUT)
serverSocket.bind((LOCAL_HOST, LOCAL_PORT))

seqNum = 0
while seqNum < TOTAL_NUM:
    receiveMsg = ""

    try:
        receiveMsg, addr = serverSocket.recvfrom(REMOTE_PORT)
    except socket.timeout as e:
        break

    if receiveMsg:
        print(receiveMsg)

    sendMsg = bytes("RETURNING " + str(seqNum) + "\n", "utf-8")
    serverSocket.sendto(sendMsg, (REMOTE_HOST, REMOTE_PORT))
    seqNum += 1
