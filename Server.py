

# Import needed libraries
from socket import socket, AF_INET, SOCK_STREAM
from thread import start_new_thread
import sys, os
HOST = ''
PORT = 9020
BUFSIZE = 4096
KILL_SERVER = False
HELP_MESSAGE = """Client request \"help<cr><lf>\" receives a response of a list of the commands and their syntax.\n
		Client request \"test: words<cr><lf>\"  receives a response of \"words<cr><lf>\".\n
		Client request \"name: <chatname><cr><lf>\" receives a response of \"OK<cr><lf>\".\n
		Client request \"get<cr><lf>\" receives a response of the entire contents of the chat buffer.\n
		Client request \"push: <stuff><cr><lf>\" receives a response of \"OK<cr><lf>\".  The result is that \"<chatname>: <stuff>\" is added as a new line to the chat buffer.\n
		Client request \"getrange <startline> <endline><cr><lf>\" receives a response of lines <startline> through <endline> from the chat buffer.\n
		Client request \"adios<cr><lf>\" will quit the current connection
		"""
#Empty list variable to store chat buffer
CHAT_BUFFER= []
serversocket = socket(AF_INET,SOCK_STREAM)
#Listen for Host on Port 9020
serversocket.bind((HOST, PORT))
#Listen for up to 5 connetions
serversocket.listen(5)

print 'Waiting for connection'

def client(sock):

    try:
        sock.send("Welcome to Chandler\'s Chat room\r\n")
        data = sock.recv(BUFSIZE)
        CHATNAME = 'unknown'

        while not data.lower().startswith('adios'):
            data_lower = data
            if data_lower.startswith('help'):
                sock.send(HELP_MESSAGE + '\r\n')
                print "got help request"

            elif data_lower.startswith("test: "):
                words = data_lower.split(": ")[1]
                sock.send(words)
                print "got test request"

            elif data_lower.startswith("name: "):
                CHATNAME = data_lower.split(': ')[1]
                sock.send("OK\r\n")
                print "got name request"

            elif data_lower.startswith("getrange"):
            	print "got getrange request"
            	#Parse argument to get ranges and save them into variables
                num_array = data_lower.split(" ")
                arg1 = int(num_array[1])
                arg2 = int(num_array[2])
                print num_array[1]
                print num_array[2]

                if arg1 < 0 or arg1 >= len(CHAT_BUFFER):
                    sock.send("Out of Range\r\n")

                elif arg2 < 0 or arg2 >= len(CHAT_BUFFER):
                    sock.send("Out of Range\r\n")

                else:
                	#Special buffer used here because of the string formatting that only
                	#occurs in the getrange function. I don't want to modify the actual
                	#CHAT_BUFFER so I use a temporary buffer instead to remove the [],'
                    ranged_buffer = []

                    #(arg2+1) will function similarly to for (i=0, i<=arg2, i++) in C++
                    #Which is needed to return the correct range.
                    for i in range(arg1, arg2+1):
                        ranged_buffer.append(CHAT_BUFFER[i])

                    print ranged_buffer #Compare with chatbuffer on server side for testing
                    ranged_buffer = str(ranged_buffer)
                    #Bunch of string formatting functions to match Ruby test script
                    #These aren't needed for the server to run but rather just formatting
                    #functions. 
                    ranged_buffer = ranged_buffer.replace('[','')
                    ranged_buffer = ranged_buffer.replace(']','')
                    ranged_buffer = ranged_buffer.replace('\'','')
                    ranged_buffer = ranged_buffer.replace(',','')
                    ranged_buffer = ranged_buffer.replace('\\r\\n','')
                    print CHAT_BUFFER #Compare with ranged_buffer to check formatting changes

                    sock.send(ranged_buffer + '\r\n')

            elif data_lower.startswith("get"):
            	print "got get request"
            	get_buffer = CHAT_BUFFER
            	get_buffer = str(get_buffer)
                get_buffer = get_buffer.replace('[','')
                get_buffer = get_buffer.replace(']','')
                get_buffer = get_buffer.replace('\'','')
                get_buffer = get_buffer.replace(',','')
                get_buffer = get_buffer.replace('\\r\\n','')

                sock.send(get_buffer + '\r\n')
                print "After sock.send()"

            elif data_lower.startswith("push: "):
            	print "got push request"
            	print str(data_lower.split(': ')[1])
            	#Add the name of the user, stringify the 1st element of the parsed command
            	#and append that to the user's name and separate everything with colons.
                CHAT_BUFFER.append(CHATNAME+': '+str(data_lower.split(': ')[1]) + '\r\n')
                sock.send("OK\r\n")

            else:
                sock.send("Error: unrecognized command: " + data_lower + "\r\n")

            #Parse next command
            data = sock.recv(BUFSIZE)

        #Close sockection for adios command
        sock.close()

    except Exception as e:
    	#Code pulled from python documentation to catch and return information about
    	#any exceptions. Used for debugging this project and future projects.
    	exc_type, exc_obj, exc_tb = sys.exc_info()
    	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    	print(exc_type, fname, exc_tb.tb_lineno)
    	print "oops!"
    	sock.send("Something Broke\r\n")
        sock.close()
        serversocket.close()

try:
    while not KILL_SERVER:
        sock,addr = serversocket.accept()
        print addr, 'is now sockected'
        start_new_thread(client,(sock,))

except:
	sock.close()
	serversocket.close()

