import json
import socket, sys, os.path, math

'''
As per Piazza post @121, I need to keep the program open for other client requests.
By placing all this in a while loop, the program can accept another connection
after resolving the previous one
'''

def MainClientConnections():
    # Starts the server program socket (not the same as client connection socket - see below)
    try:
        ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Starting server...")
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

    #backlog value is from 0 to 5
    ServerSock.listen(1)

    # conn: the clients connection to the server. Data is sent through this
    while True:

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
            continue

        # split header into respective parts
        headerList = client_request.split("\r\n")
        # Requested route with query parameters
        API_call = headerList[0].split(" ")[1].split("?")
        route = API_call[0].strip("/")

        # if requested route != product, send 404 response code
        if(route != "product"):
            response = GenerateResponse(404)
            conn.send(response.encode("utf-8"))
            sys.stderr.write("Closed connection with client")
            conn.close()
            continue

        # if no parameters detected, send 400 response code, else set query parameters
        query_params = []
        try:
            query_params = API_call[1].split("&")

        except IndexError as err:
            response = GenerateResponse(400)
            conn.send(response.encode("utf-8"))
            sys.stderr.write("Closed connection with client")
            conn.close()
            continue

        # convert argument array to float values
        num_arr = StrArrToNumArr(query_params)
        # send 400 response code if cannot convert argument to float, else send 200 response code
        if(num_arr == False):
            response = GenerateResponse(400)
            conn.send(response.encode("utf-8"))
            sys.stderr.write("Closed connection with client")
            conn.close()
            continue
        else:
            prod = CalculateProduct(num_arr)
            response = GenerateResponse(200, [prod, num_arr])
            conn.send(response.encode("utf-8"))
            conn.close()
            continue


        # sys.stdout.write(client_request)

        # Close the connection with the client


#handle code response / output
def GenerateResponse(statusCode, query_params=[]):

    response = ""
    response_body = {
        "operation": "product"
    }
    if statusCode == 200:
        # Calculate product and get number array

        response_body["operands"] = query_params[1]
        response_body["result"] = query_params[0]
        response_body = json.dumps(response_body)

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

    elif statusCode == 400:
        response += "HTTP/1.0 400 Bad Request\r\n"
        response += "\r\n"
        response += "<html><head>" \
                    "<title>400 Bad Request</title>" \
                    "</head><body>" \
                    "<h1>Not Found</h1>" \
                    "<p>The requested URL included incorrect parameters</p>" \
                    "</body></html>"

    return response

# convert string argument array to float values
def StrArrToNumArr(argument_arr):
    num_arr = []
    for arg in argument_arr:
        split_arg = arg.split("=")
        num = split_arg[1]

        # if a given parameter is not a number, send response code 400
        try:
            num = float(num)
        except ValueError as err:
            sys.stderr.write("ERROR: unable to convert argument to float value")
            return False
        num_arr.append(num)
    return num_arr

# function to calculate product of given arguments
def CalculateProduct(argument_arr):
    product = 1
    for i in argument_arr:
        # while calculating product, if product exceeds number limit, set product as infinity
        try:
            product *= i
        except OverflowError as err:
            product = "inf"
            break

    return product



if __name__ == "__main__":
    MainClientConnections()
