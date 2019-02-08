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

from freetests import BASEPORT
import random
import re
import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse

def help():

    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):

    def __init__(self, code = 200, body = ""):

        self.code = code
        self.body = body
        
    def __str__(self):

        return str(self.code) + ", " + self.body

class HTTPClient(object):

    # Mark the socket closed.
    def close(self):

        self.socket.close()

    def command(self, url, command = "GET", args = None):

        if (command == "POST"):

            return self.POST(url, args)

        else:

            return self.GET(url, args)

    # Connect to a remote socket at address.
    def connect(self, host, port):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def GET(self, url, args = None):

        hostname, port, path = self.parse_url(url)

        self.connect(hostname, port)

        request = self.get_request(hostname, path, "", "GET ")

        self.sendall(request)

        data = self.recvall()
        status_code = self.get_code(data)
        content = self.get_body(data)

        self.close()
        
        return HTTPResponse(status_code, content)

    def get_body(self, data):

        try:

            body = data.split("\r\n\r\n")[1]

        except:

            body = ''

        return body

    # Get the status code: 2xx, 3xx, 4xx, 5xx
    def get_code(self, data):

        try:

            status_code = int(data.split(" ")[1])

        except:

            status_code = 400

        return status_code

    def get_port(self, port, scheme):

        if scheme == "http":

            return 80

        elif scheme == "https":

            return 443

        else:

            return BASEPORT

    # Tranform dictionary into key and value lists.
    def get_query(self, args):

        keys = list(args.keys())
        values = list(args.values())
        query = ''
        
        for i in range(len(keys)):

            query += keys[i] + '=' + values[i] + '&'
            
        query = query[:-1]

        return query

    def get_request(self, hostname, path, query, method):

        if method == "POST ":

            method += path + " HTTP/1.1\r\n"
            host = "Host: " + hostname + "\r\n"
            content_length = "Content-Length: " + str(len(query)) + "\r\n"
            content_type = "Content-Type: application/x-www-form-urlencoded\r\n"
        
            if len(query) > 0:

                connection = "Connection: close\r\n\r\n" + query + "\r\n"

            else:
            
                connection = "Connection: close\r\n\r\n"

            return method + host + content_length + content_type + connection

        else:

            method += path + " HTTP/1.1\r\n"
            host = "Host: " + hostname + "\r\n"
            connection = "Connection: close\r\n\r\n"

            return method + host + connection

    # https://docs.python.org/3/library/urllib.parse.html#url-parsing
    def parse_url(self, url):

        parsedURL = urllib.parse.urlparse(url)
        scheme = parsedURL.scheme
        hostname = parsedURL.hostname
        port = parsedURL.port
        path = parsedURL.path
        
        if path == "":

            path = "/"

        if port == None:

            port = self.get_port(port, scheme)

        return hostname, port, path

    def POST(self, url, args = None):

        hostname, port, path = self.parse_url(url)

        self.connect(hostname, port)
        
        if (args != None):

            # query = self.get_query(args)
            query = urllib.parse.urlencode(args)
            request = self.get_request(hostname, path, query, "POST ")

        else:
            
            request = self.get_request(hostname, path, "", "POST ")
    
        self.sendall(request)

        data = self.recvall()
        status_code = self.get_code(data)
        content = self.get_body(data)

        self.close()        

        return HTTPResponse(status_code, content)

    # Read everything from the socket.
    def recvall(self):

        buffer = bytearray()
        done = False

        while not done:

            part = self.socket.recv(1024)

            if (part):

                buffer.extend(part)

            else:

                done = not part

        return buffer.decode('utf-8')
    
    # Send data to the socket.
    def sendall(self, data):

        self.socket.sendall(data.encode('utf-8'))
    
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