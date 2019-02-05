#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import random
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):

    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    #def get_host_port(self,url):

    def parse_url(self, url):

        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        path = parsed.path
        port = parsed.port
        scheme = parsed.scheme

        return host, path, port, scheme

    def get_port(self, port, scheme):

        if scheme == "http":
            return 80
        elif scheme == "https":
            return 443
        else:
            return (27600 + random.randint(1,100))

    def connect(self, host, port):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(host)
        print(port)
        
        
        self.socket.connect((host, port))

    def get_code(self, data):

        try:
            code = int(data.split("")[1])
        except:
            code = 400

        return code

    def get_headers(self,data):

        try:
            headers = data.split("\r\n\r\n")[0]

        except:
            headers = ""

        return headers

    def get_body(self, data):

        body = data.find("\r\n\r\n")
        
        if body != -1:
            return data[body + 4:]
        else:
            return ('')
    
    def sendall(self, data):

        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):

        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):

        buffer = bytearray()
        done = False

        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):

        GET_scheme, GET_host, GET_port, GET_path = self.parse_url(url)
        
        
        if GET_port == None:
            GET_port = self.get_port(GET_port, GET_scheme)
            
        self.connect(GET_host, GET_port)
        
        # To handle http://Slashdot.org
        if GET_path == "":
            GET_request = "GET / HTTP/1.1\nHost: " + GET_host + "\n\n"
        else:
            GET_request = "GET " + GET_path + " HTTP/1.1\nHost: " + GET_host + "\n\n"
        
        self.sendall(GET_request)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        #print(body)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        POST_scheme, POST_host, POST_port, POST_path = self.parse_url(url)
        self.connect(POST_host, POST_port)
        
        if (args != None):
            dictlist = []
            args = list(args.items())
            for key, value in args:
                temp = key + "=" + value
                dictlist.append(temp)
            args = "&".join(dictlist)
            POST_request = "POST " + POST_path + " HTTP/1.1\nHost: " + POST_host + "\nContent-Length: " + str(len(args)) + "\nContent-Type: application/x-www-form-urlencoded" + "\n\n" + args + "\n"         
        else:
            POST_request = "POST " + POST_path + " HTTP/1.1\nHost: " + POST_host + "\nContent-Length: 0" + "\nContent-Type: application/x-www-form-urlencoded" + "\n\n"
            
        self.sendall(POST_request)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)

        self.close()        
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):

        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)
    
if __name__ == "__main__":

    client = HTTPClient()
    command = "GET"

    if (len(sys.argv) <= 1):

        help()
        sys.exit(1)

    elif (len(sys.argv) == 3):

        print(client.command(sys.argv[2], sys.argv[1]))

    else:

        print(client.command(sys.argv[1]))
