#!/usr/bin/env python3
import socketserver
import urllib.parse
import json, os, sys


"""
Written by: Raymon Skjørten Hansen
Email: raymon.s.hansen@uit.no
Course: INF-2300 - Networking
UiT - The Arctic University of Norway
May 9th, 2019
"""
msg_id = 1
datalist = []
class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    This class is responsible for handling a request. The whole class is
    handed over as a parameter to the server instance so that it is capable
    of processing request. The server will use the handle-method to do this.
    It is instantiated once for each request!
    Since it inherits from the StreamRequestHandler class, it has two very
    usefull attributes you can use:

    rfile - This is the whole content of the request, displayed as a python
    file-like object. This means we can do readline(), readlines() on it!

    wfile - This is a file-like object which represents the response. We can
    write to it with write(). When we do wfile.close(), the response is
    automatically sent.

    The class has three important methods:
    handle() - is called to handle each request.
    setup() - Does nothing by default, but can be used to do any initial
    tasks before handling a request. Is automatically called before handle().
    finish() - Does nothing by default, but is called after handle() to do any
    necessary clean up after a request is handled.
    """

    def handle(self):
        """
        This method is responsible for handling an http-request. You can, and should(!),
        make additional methods to organize the flow with which a request is handled by
        this method. But it all starts here!
        """
        # Reads the stream of data
        input_data = self.rfile.readline().split()

        # Puts the initial stream into a dictionary
        self.data = {"Request": input_data[0], "path": input_data[1], "http-type": input_data[2]}
        # Puts the rest of the lines into the same dictionary
        while len(input_data) != 0 and input_data !='\r\n':
            input_data = self.rfile.readline().split()
            if len(input_data) != 0:
                key = input_data[0].strip(b":")
                self.data[key] = input_data[1]

        ### Debugging
        print("{} requested: {}".format(self.client_address[0], self.data["Request"]))

        ### RESTApi
        # If the "request" was a GET request, call GET handler
        if self.data["Request"] == b'GET':
            self.GET_handler()

        # If the "request" was a POST request, call POST handler
        elif self.data["Request"] == b'POST':
            self.POST_handler()

        # If the "request" was a PUT request, call PUT handler
        elif self.data["Request"] == b'PUT':
            self.PUT_handler()

        # If the "request" was a DELETE request, call DEL handler
        elif self.data["Request"] == b'DELETE':
            self.DEL_handler()

    def GET_handler(self):
        #initialize some operands
        self.filename = ""
        self.response = ""
        self.contenttype = b"text/html"

        # If match then its the index 
        if self.data["path"] == b'/' or self.data["path"] == b'/index.html' or self.data["path"] == '/index':
            self.filename = 'index.html'

        # If match then its a message
        elif self.data["path"] == b'/messages' or self.data["path"] == b'/messages.json':
            self.filename = 'messages.json'
            self.contenttype = b'text/json'

        elif self.data["path"] == b'/server.py' or self.data["path"] == b'server.html' or self.data["path"] == b'server':
            self.filename = '403error.html'
            self.length = len(self.filename)
            self.error403()

        else:
            self.filename = self.data["path"].strip(b'/')

        try:
            with open(self.filename, 'rb') as f:
                self.page = f.read()
                self.length = len(self.page)
            self.OK200()

            # Checking content type
            if self.contenttype != 'text/json':
                self.response += self.page
            else:
                # Getting json elements
                pass

        except IOError:
            self.error404()

        finally:
            # Return return_msg
            self.wfile.write(self.response)


    ### Text
    # def POST_handler(self):
    #    return_msg = 0
    #    self.contenttype = b'text/plain; charset=utf-8'

    #    # Find length of content
    #    self.length = self.data[b'Content-Length']
    #    # Read said length
    #    return_msg = str(self.rfile.read(int(self.length)))

    #    # Crop and parse correctly
    #    return_msg = return_msg [7:-1]
    #    return_msg = urllib.parse.unquote_plus(return_msg) + '\n'

    #    try:
    #        # Append return_msg to file
    #        with open("test.txt", "a") as file:
    #            file.write(return_msg)

    #    except IOError:
    #        # If file doesnt exist write as if it was there
    #        # which will make the file
    #        with open("test.txt", "w") as file:
    #            file.write(return_msg)

    #    finally:
    #        self.OK200()
    #        with open('test.txt', 'rb') as f:
    #            text = f.read()
    #        self.response += text
    #        self.wfile.write(self.response)

    ### JSON
    def POST_handler(self):
        global msg_id,datalist
        return_msg = 0
        self.contenttype = b'text/plain; charset=utf-8'

        # Find length of content
        self.length = self.data[b'Content-Length']
        # Read said length
        return_msg = str(self.rfile.read(int(self.length)))
        # Crop and parse correctly
        # return_msg = return_msg [7:-1]
        return_msg = {
           "id": msg_id,
           "text": return_msg[7:][:-1]
        }
        datalist.append(return_msg)
        # return_msg = urllib.parse.unquote_plus(return_msg) + '\n'
        if self.data["path"] == b'/test.txt':
            try:
               # Append return_msg to file
                f = open("test.txt","a")
                f.write(return_msg['text']+"\r\n")
                f.close()


            except IOError:
               # If file doesnt exist write as if it was there
               # which will make the file
                with open("test.txt", "w") as f:
                   f.write(str(return_msg['text'])+"\r\n")
                   f.close()
            finally:
                self.OK200()
                with open('test.txt', 'rb') as f:
                    text = f.read()
                self.response += text
                self.wfile.write(self.response)   
        elif self.data["path"] == b'/messages' :
            try:  
                with open("messages.json", "w") as file:
                    json.dump(datalist, file)
                    msg_id += 1  
                with open("tmp.json","w") as tmp:
                    json.dump(return_msg,tmp)
            finally:
                self.OK200()
                with open('tmp.json', 'rb') as f:
                    text = f.read()
                self.wfile.write(self.response)  
                self.response = text
                self.wfile.write(self.response) 
        else:
            self.error403()
            


    def PUT_handler(self):
        global msg_id,datalist
        return_msg = 0
        self.contenttype = b'text/plain; charset=utf-8'

        # Find length of content
        self.length = self.data[b'Content-Length']
        # Read said length
        return_msg = str(self.rfile.read(int(self.length)))
        # Crop and parse correctly
        # return_msg = return_msg [7:-1]
        dataid = return_msg.split('&')[0][5:]
        datatext = return_msg.split('&')[1][5:][:-1]
        for info in datalist:
            if str(info['id']) in str(dataid):
                info['text'] = datatext
                break
        with open("messages.json", "w") as file:
                    json.dump(datalist, file)
        self.OK200()
        with open('messages.json', 'rb') as f:
            text = f.read()
        self.wfile.write(self.response)  
        self.response = text
        self.wfile.write(self.response)

    def DEL_handler(self):
        global msg_id,datalist
        return_msg = 0
        self.contenttype = b'text/plain; charset=utf-8'

        # Find length of content
        self.length = self.data[b'Content-Length']
        # Read said length
        return_msg = str(self.rfile.read(int(self.length)))
        # Crop and parse correctly
        # return_msg = return_msg [7:-1]
        dataid = return_msg[5:][:-1]
        tmp = []
        flag=False
        for info in datalist:
            if str(info['id']) in str(dataid):
                flag=True
                continue
            else:
                # if flag==True:
                #     info['id']-=1    
                tmp.append(info)    
        datalist=tmp       
        with open("messages.json", "w") as file:
                    json.dump(datalist, file)
        self.OK200()
        with open('messages.json', 'rb') as f:
            text = f.read()
        self.wfile.write(self.response)  
        self.response = text
        self.wfile.write(self.response)

    def OK200(self):
        # Returns 200 ok response
        self.response = b'HTTP/1.1 200 OK\r\n'
        self.response += b'Content-Type: '+ self.contenttype + b'\r\n'
        self.response += b'Content-Length: '+ str(self.length).encode("utf-8") + b'\r\n'
        self.response += b'\r\n'

    def error404(self):
        # Returns 404 not found error
        length = len(b'<h1>404 - NOT FOUND</h1>')
        self.response = b'HTTP/1.1 404 NOT FOUND\r\n'
        self.response += b'Content-Type: text/html\r\n'
        self.response += b'Content-Length: '+ str(length).encode("utf-8") +b'\r\n'
        self.response += b'\r\n'
        self.response += b'<h1>404 - NOT FOUND</h1>'

    def error403(self):
        # Returns 403 no access response
        self.response = b'HTTP/1.1 403 NO ACCESS\r\n'
        self.response += b'Content-Type: text/html\r\n'
        self.response += b'Content-Length: '+ str(self.length).encode("utf-8") + b'\r\n'
        self.response += b'\r\n' 

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()
