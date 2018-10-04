

# Import needed libraries
from socket import *
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])
ADDR = (HOST,PORT)
BUFSIZE = 4096

#create an INET, STREAMing socket
s = socket(AF_INET, SOCK_STREAM)
#now connect to the web server on port 9020
# - the normal http port
s.connect((ADDR))
try:
#recieves welcome message
    data = s.recv(BUFSIZE)
    print data

#send commands to server loop
    toSend = ''
    while toSend != 'adios': #TODO this need to break out off of the message that is sent back from the server
        toSend = raw_input("-->")
        s.send(toSend + '\r\n')
        output = s.recv(BUFSIZE)
        print output

    s.close()
except:
    s.close()
