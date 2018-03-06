# telnet program example
import socket, select, string, sys
 
#main function
if __name__ == "__main__":
     
    if (len(sys.argv) == 1):
        print('Usage : python client.py hostname port')
        print("Using default values localhost and port 5000")
        host = "localhost"
        port = 5000
    elif(len(sys.argv) < 3) :
        print('Usage : python client.py hostname port')
        sys.exit()
    else:
	    host = sys.argv[1]
	    port = int(sys.argv[2])

     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print('Unable to connect')
        sys.exit()
     
    print('Connected to remote host. Start sending messages')

    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [], 0)
         
        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print('\nDisconnected from chat server')
                    sys.exit()
                else :
                    # print data
                    sys.stdout.write("<Server> " + data.decode("utf-8"))
             
            #user entered a message
            else :
                msg = sys.stdin.readline()
                s.send(str.encode(msg))
