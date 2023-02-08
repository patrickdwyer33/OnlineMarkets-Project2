#http_server2.py
#Part 3: muilti-connection web server
import socket
import os
import sys
import select

#Steps:
#   1. Create TCP socket
#   2. Bind socket to proviced port
#   3. Listen to socket (accept socket)
#   4. Initialize list of open connections
#   5. Repeat:
#       a. Make list of sockets (list of all open connections)
#       b. Add accept socket to read list
#       c. Call select system call with read list
#       d. For each readable socket:
#           i. if accept socket -> accept the new connction, add to list
#           ii. if other socket -> read http, parse, check file, construct response

#Resources:
# http_server1 code, https://pymotw.com/3/select/

def Main():
    # Starts the server program socket (not the same as client connection socket - see below)
    try:
        Server2Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Server2Sock.setblocking(0)

    except socket.error as e:
        sys.stderr.write("ERROR: Unable to create socket!")
        sys.stderr.write(e)
        sys.exit(1)

    #set host and port vals
    host = ""
    port = int(sys.argv[1])

    #attempted binding
    try:
        Server2Sock.bind((host, port))

    except socket.error as e:
        sys.stderr.write(f"ERROR: Unable to bind socket - {e}")
        sys.exit(1)

    #backlog value is either 1 or 5
    Server2Sock.listen(5)


    #initialize openConnections list, readList, and message queue
    openConnections = [] #also known as outputs (expected to write)
    readList = [Server2Sock] #ready to be read

    #must keep client's requests in queue to be processed
    #(just like client_request in http_server1)
    message_queue = {}

    #only happens when there is stuff available to read
    while readList:
        #get out distinguished connections
        readable, writeable, exceptional = select.select(readList, openConnections, readList)
        #handle readable Content
        for s in readable:

            #check if equal to accept socket
            if s is Server2Sock:
                conn, address = s.accept()
                conn.setblocking(0)
                readList.append(conn) #add to readable

            #else we need to read HTTP data
            else:
                #so we can add data
                if s not in message_queue:
                    message_queue[s] = ""
                # Keep reading data from client connection and put into 'request' variable
                # (just like http_client)
                while True:
                    req_data = s.recv(1024).decode()
                    if not req_data:
                        #if no data, and its open -> remove it its useless
                        if s in openConnections:
                            openConnections.remove(s)
                        break
                    #keep track os specific request
                    message_queue[s] += req_data

                    if "\r\n\r\n" in message_queue[s]:
                        #we have reached end, make open
                        openConnections.append(s)
                        break

        #handle the writes from openConnections, parsing and checking path
        for s in writeable:
            #if no message, remove from open
            if s not in message_queue:
                openConnections.remove(s)
                continue

            #parse request
            # split header into respective parts
            headerList = message_queue[s].split("\r\n")
            # Requested file from client
            GetFile = headerList[0].split(" ")[1].split("/", 1)[-1]

            # Check if file exists in working directory
            if os.path.exists(GetFile):
                #file exits but doesnt have .htm or .html extension
                if ".htm" not in GetFile or ".html" not in GetFile:
                    s.send(GenerateResponse(GetFile, 403).encode('utf-8'))
                else:
                    s.send(GenerateResponse(GetFile, 200).encode('utf-8'))
            elif not os.path.exists(GetFile):
                response = GenerateResponse(GetFile, 404)
                s.send(response.encode('utf-8'))

            #connection finished writing / reading, close
            if s in openConnections:
                openConnections.remove(s)
            if s in readList:
                readList.remove(s)

            #clear from message queue
            if s in message_queue:
                del message_queue[s]

            #close socket
            s.close()
            sys.stderr.write("Closed connection with client")

        #handle error connections
        for s in exceptional:
            readList.remove(s)
            if s in openConnections:
                openConnections.remove(s)

            s.close()
            del message_queue[s]

#handle code response / output
#taken from http_server1.py
def GenerateResponse(fileName, statusCode):

    response = ""
    if statusCode == 200:
        # open the html file
        f = open(fileName, "r")
        response_body = f.read()

        response += "HTTP/1.0 200 OK\r\n"
        response += "Content-Type: text/html; encoding=utf8\r\n"
        response += f"Content-Length: {len(response_body)}\n"
        response += "\r\n"
        response += response_body

    elif statusCode == 404:
        response += "HTTP/1.0 404 Not Found\r\n"
        response += "\r\n"
        response += "<html><head>" \
                    "<title>404 Not Found</title>" \
                    "</head><body>" \
                    "<h1>Not Found</h1>" \
                    "<p>The requested URL was not found on this server.</p>" \
                    "</body></html>"

    elif statusCode == 403:
        response += "HTTP/1.0 403 Forbidden\r\n"
        response += "\r\n"
        response += "<html><head>" \
                    "<title>403 Forbidden</title>" \
                    "</head><body>" \
                    "<h1>Forbidden</h1>" \
                    "<p>The requested URL was not of type htm or html.</p>" \
                    "</body></html>"

    return response


if __name__ == "__main__":
    Main()
