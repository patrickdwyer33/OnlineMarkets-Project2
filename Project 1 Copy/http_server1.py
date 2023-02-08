import socket, sys, os.path

'''
As per Piazza post @121, I need to keep the program open for other client requests.
By placing all this in a while loop, the program can accept another connection
after resolving the previous one
'''

def MainClientConnections():
    # Starts the server program socket (not the same as client connection socket - see below)
    try:
        ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error as e:
        sys.stderr.write("ERROR: Unable to create socket!")
        sys.stderr.write(e)
        sys.exit(1)

    #set host and port vals
    host = ""
    port = int(sys.argv[1])

    try:
        ServerSock.bind((host, port))

    except socket.error as e:
        sys.stderr.write(f"ERROR: Unable to bind socket - {e}")
        sys.exit(1)

    #backlog value is either 1 or 5
    ServerSock.listen(5)

    # conn: the clients connection to the server. Data is sent through this
    #while True:

    conn, address = ServerSock.accept()
    client_request = ''
    # Keep reading data from client connection and put into 'request' variable (just like http_client)
    while True:
        req_data = conn.recv(1024).decode()
        if not req_data:
            break
        client_request += req_data
        if "\r\n\r\n" in client_request:
            #we have reached end
            break

    #check if there still exists a client request
    if client_request == '':
        conn.close()
        #continue

    # split header into respective parts
    headerList = client_request.split("\r\n")
    # Requested file from client
    GetFile = headerList[0].split(" ")[1].split("/", 1)[-1]

    # Check if file exists in working directory
    if os.path.exists(GetFile):
        #file exits but doesnt have .htm or .html extension
        if ".htm" not in GetFile or ".html" not in GetFile:
            conn.send(GenerateResponse(GetFile, 403).encode('utf-8'))
        else:
            conn.send(GenerateResponse(GetFile, 200).encode('utf-8'))
    elif not os.path.exists(GetFile):
        response = GenerateResponse(GetFile, 404)
        conn.send(response.encode('utf-8'))
        # sys.stdout.write(client_request)

        # Close the connection with the client
    conn.close()
    sys.stderr.write("Closed connection with client")

#handle code response / output
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
    MainClientConnections()

#sys.exit(0) # I need to figure out where to put this (infinite while loop makes this unreachable)
