
#!/usr/bin/python
from socket import socket, AF_INET, SOCK_STREAM
from thread import start_new_thread
HOST = ''
PORT = 9020
ADDR = (HOST,PORT)
BUFSIZE = 4096
KILL_SERVER = False
HELP_MESSAGE = """Client request \"help<cr><lf>\" receives a response of a list of the commands and their syntax.\n
		Client request \"test: words<cr><lf>\"  receives a response of \"words<cr><lf>\".\n
		Client request \"name: <chatname><cr><lf>\" receives a response of \"OK<cr><lf>\".\n
		Client request \"get<cr><lf>\" receives a response of the entire contents of the chat buffer.\n
		Client request \"push: <stuff><cr><lf>\" receives a response of \"OK<cr><lf>\".  The result is that \"<chatname>: <stuff>\" is added as a new line to the chat buffer.\n
		Client request \"getrange <startline> <endline><cr><lf>\" receives a response of lines <startline> through <endline> from the chat buffer.\n
		Client request \"adios<cr><lf>\" will quit the current connection\r\n
		"""
CHAT_BUFFER= []
#create an INET, STREAMing socket
serversocket = socket(AF_INET,SOCK_STREAM)
#bind the socket to a public host,
# and a well-known port
serversocket.bind((ADDR))
#become a server socket
serversocket.listen(5)

print 'waiting for connection request'

def clientthread(conn):

    try:
        conn.send('Welcome to Bryson\'s Chat room\r\n')

        data = conn.recv(BUFSIZE)

        CHATNAME = 'unknown'
        while not data.lower().startswith('adios'):
            cleaned = data.lower()
            if cleaned.startswith('help'):
                conn.send(HELP_MESSAGE)
            elif cleaned.startswith("test: "):
                words = cleaned.split(': ')[1]
                conn.send(words+'\r\n')
            elif cleaned.startswith("name: "):
                CHATNAME = cleaned.split(': ')[1]
                conn.send('OK\r\n')
            elif cleaned.startswith("getrange "):
                numbers = cleaned.split()
                one = int(numbers[1])
                two = int(numbers[2])
                if one < 0 or one >= len(CHAT_BUFFER):
                    conn.send('Out of Range\r\n')
                elif two < 0 or two >= len(CHAT_BUFFER):
                    conn.send('Out of Range\r\n')
                else:
                    chat_ranged = []
                    for i in range(one, two):
                        chat_ranged.append(CHAT_BUFFER[i])
                    import pprint
                    pp = pprint.PrettyPrinter(width=30)
                    conn.send(pp.pformat(chat_ranged)+'\r\n')
            elif cleaned.startswith("get"):
                import pprint
                pp=pprint.PrettyPrinter(width=30)
                conn.send(pp.pformat(CHAT_BUFFER)+'\r\n')
            elif cleaned.startswith("push: "):
                CHAT_BUFFER.append(CHATNAME+': '+str(cleaned.split(': ')[1]))
                conn.send('OK\r\n')
            elif cleaned.startswith("kill it clean"):
                KILL_SERVER=True
                conn.send('OK\r\n')
            else:
                conn.send('did not understand\r\n')
            data = conn.recv(BUFSIZE)
        conn.close()
    except:
        conn.send("Something Broke\r\n")
        conn.close()
try:
    while not KILL_SERVER:
        conn,addr = serversocket.accept()
        print 'it is now connected'
        start_new_thread(clientthread,(conn,))
except:
   serversocket.close()
