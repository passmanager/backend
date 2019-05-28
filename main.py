import http.server
import socketserver
import re
import os
import json

PORT = 8000
passwordsDir = "passwords" + os.sep

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        
        if (self.path == "/"):
            self.send_response(200)
            self.send_header('Content-type', "text/plain")
            self.end_headers()
            self.wfile.write(str.encode("This server doesn't contain UI"))
            return 
        pattern = re.compile("\/user\/[^\/]*\/$")
        if pattern.match(self.path):
            try:
                files = os.listdir(self.path[1:] + passwordsDir)
                self.send_response(200)
                self.send_header('Content-type', "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "x-requested-with")
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.end_headers()
                global json
                files = sorted(files, key=lambda s: s.casefold())
                self.wfile.write(json.dumps(files).encode('utf-8'))
                return 
            except Exception as ex:
                print('get all passwords list')
                print(type(ex).__name__)
                print(ex)
                self.send_error(404, "username not found")
                self.end_headers()
                return 
        pattern = re.compile("\/user\/[^\/]*\/.*")
        if pattern.match(self.path):
            try:
                username = self.path.split('/')[1] + "/" + self.path.split('/')[2]
                password = "".join(['⁄' if word == "" else word for word in self.path.split('/')[3:]]) #not forward slash but an unicode char 2044 ⁄, used because forward slash is seperating files
                if (password[-1] == '⁄'):
                    password = password[:-1]
                password = password.replace("%20", " ")
                if not os.path.isfile(username + os.sep + passwordsDir + password):
                    self.send_error(404, password.replace('⁄', '/') + " not found")
                    self.end_headers()
                    return 
                entry = open(username + os.sep + passwordsDir + password)
                self.send_response(200)
                self.send_header('Content-type', "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "x-requested-with")
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.end_headers()
                data = entry.read()
                temp = dict()
                temp['usernameSalt'] = data.split('\n')[0]
                temp['username'] = data.split('\n')[1]
                temp['passwordSalt'] = data.split('\n')[2]
                temp['password'] = data.split('\n')[3]

                self.wfile.write(json.dumps(temp).encode('utf-8'))
                entry.close()
                return 
            except Exception as ex:
                print('get single password')
                print(type(ex).__name__)
                print(ex)
                return
        self.send_error(404, "Specify user with / at the end")
        self.end_headers()
        return


handler = MyHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    try:
        print("Serving at port: " + str(PORT))
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.socket.close()
        print("Shutting down")
