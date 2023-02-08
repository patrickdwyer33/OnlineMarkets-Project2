#http_client.py
import socket
import sys

#deal with imported PORT numbers

#need to:
# 1. check input call for errors
# 2. parse through url
#   - extract host and path
# http://somewebsite.com/path/page.html
#   Turn into -> http, somewebsite.com, path/page.html

# 3. setup socket
# 4. send data from parsed url to socket
# 5. receive back and print out HTML data
# 6. account for redirects
# 7. return exit code

redirectNum = 0; #global var storing num of redirects

#this function will handle our redirects and rerun Main
def redirectHandler(headerList):

    #need to keep track of all redirects
    global redirectNum
    redirectNum += 1;

    #limit redirects, too many -> exit
    if(redirectNum > 10):
        sys.stderr.write("Error: Too many redirects\n")
        sys.exit(1)

    #find location from header
    #must get real url from header in "Location:"
    for head in headerList:
        if head.split(" ")[0] == "Location:":
            #store new url
            redirectedURL = head.split(" ")[1]
            break

    #must check if redirect to bad page (same as initial url checks)
    if not redirectedURL.__contains__("://"):
        sys.stderr.write("Error: Random string inputs, not URL\n")
        sys.exit(1)
    elif redirectedURL.split("://")[0] == "https":
        sys.stderr.write("Error: Attempting to reach HTTPS\n")
        sys.exit(1)
    elif redirectedURL.split("://")[0] != "http":
        sys.stderr.write("Error: URL does not start with HTTP\n")
        sys.exit(1)

    #run rest of our code on new URL
    Main(redirectedURL)

#function that returns the type found in the Content-Type: field
def typeFound(headerList):
    #find content-type in header
    for head in headerList:
        if head.split(";")[0].split(" ")[0] == "Content-Type:":
            return head.split(";")[0].split(" ")[1]


def Main(designatedURL):
#Step 2: Parse url
#Input: http://somewebsite.com/path/page.html

    # Message Header:
    # GET /path/page.html HTTP/1.0
    # Host: somewebsite.com
    # blank line

    #get url after http
    parse1 = designatedURL.split("://")[1]

    #this means there is a port present in url
    if ":" in parse1:
        #get port number from in between ":" and "/" (must be int)
        PORT = int(parse1.split(":")[1].split("/")[0])
        HOST = parse1.split(":")[0]
        REST = parse1.split("/")[1:]
    #if not port number, handle differently
    else:
        #split up by slashes, first element is your host
        #there is a path present, must do more work
        if parse1.__contains__("/"):
            HOST = parse1.split("/")[0]
            REST = parse1.split("/")[1:]
        #no specified path, only element is url name
        else:
            HOST = parse1
            PATH = "/"
            REST = []

        PORT = 80 #standard port

    #put path back together from elements in REST
    PATH = ""
    if REST:
        for element in REST:
            PATH += "/"
            PATH += element

    #format into GET call
    httpGET = "GET " + PATH + " HTTP/1.0\r\n"
    httpGET += "Host: " + HOST + "\r\n"
    httpGET += "\r\n"

    print(HOST)
    print(PORT)
    #now that we have GET call, we can move on
    #socket creation
    #AF_INET is for IPv4
    #SOCK_STREAM is for HTTP
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #setup socket: connect to our host address
    #add try just in case fails to connect
    try:
        socketClient.connect((HOST, PORT))
    except:
        sys.stderr.write("Error: Failed to connect\n")
        sys.exit(1)

    #send GET call (must encode in bytes)
    try:
        socketClient.send(httpGET.encode('utf-8'))
    except:
        sys.stderr.write("Error: Failed to send data\n")
        sys.exit(1)

    #receive response from server
    htmlContent = '' #hold all our html we want printed out

    #account for larger, multi-page text, while loop
    while True:
        #get data from socket (have to decode from bytes)
        data = socketClient.recv(1024).decode()
        #stop loop when data is over
        if not data:
            break
        htmlContent += data;

    #now that we have our data and it looks good, we move onto our message codes
    #look at redirects
    #check content-type

    #get code from first line & message code
    firstLine = htmlContent.split("\r\n")[0]
    messageCode = firstLine.split()[1]

    #code to seperate body from Header
    splitData = htmlContent.split("\r\n\r\n")
    #body is everything comes before
    body = splitData[1]
    #get each line of header put into list
    headerList = splitData[0].split("\r\n")

    #exit with non-zero code if wrong content found
    if typeFound(headerList) != "text/html":
        sys.stderr.write("Wrong content-type found.")
        sys.exit(1)

    #if code = 200 -> return exit code 0 (print output)
    if  int(messageCode) == 200:
        print(body)
        socketClient.close() #close socket, done
        sys.exit(0) #all good

    #if code = 301 or 302 -> redirect, fetch connected result, print stderr
    elif int(messageCode) == 301 or int(messageCode) == 302:
        #redirect to proper URL (call to function)
        redirectHandler(headerList)
        sys.exit(0)

    #if code = 404 -> print body, exit with non zero code
    elif int(messageCode) == 404:
        print(body)
        socketClient.close() #close socket, done
        sys.exit(1) #bad

    #some other code -> exit with non zero code
    else:
        socketClient.close() #close socket, done
        sys.exit(1) #bad
    #stop after 10 redirects

#handle input for type errors
#happens when not correct amount of args
if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.stderr.write("Error: No URL present\n")
        sys.exit(1)
    inputURL = sys.argv[1] #comes in as string
    #check for HTTPS
    if not inputURL.__contains__("://"):
        sys.stderr.write("Error: Random string inputs, not URL\n")
        sys.exit(1)
    elif inputURL.split("://")[0] == "https":
        sys.stderr.write("Error: Attempting to reach HTTPS\n")
        sys.exit(1)
    #check if bad file extension
    elif inputURL.split("://")[0] != "http":
        sys.stderr.write("Error: URL does not start with HTTP\n")
        sys.exit(1)
    #end of argument check, now we should have everything we need
    #call our main funciton on our inputed URL
    Main(inputURL)
