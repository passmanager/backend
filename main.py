import http.server
import socketserver
import re
import os

PORT = 8000
passwordsDir = "passwords" + os.sep

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        
        if (self.path == "/"):
            self.send_response(200)
            self.send_header('Content-type', "text/html")
            self.end_headers()
            self.wfile.write(str.encode("This server doesn't contain UI"))
            return 
        pattern = re.compile("\/.*\/$")
        if pattern.match(self.path):
            try:
                files = os.listdir(self.path[1:] + passwordsDir)
                self.send_response(200)
                self.send_header('Content-type', "text/html")
                self.end_headers()
                stringToReturn = ""
                for i in files:
                    stringToReturn += i + "\n"
                self.wfile.write(str.encode(stringToReturn))
                return 
            except:
                self.send_error(404, "username not found")
                self.end_headers()
                return 
        pattern = re.compile("\/.*\/.*$")
        if pattern.match(self.path):
            try:
                username = self.path.split('/')[1]
                password = self.path.split('/')[2]
                if not os.path.isfile(username + os.sep + passwordsDir + password):
                    self.send_error(404, "Password entry not found")
                    return 
                entry = open(username + os.sep + passwordsDir + password)
                self.send_response(200)
                self.send_header('Content-type', "text")
                self.end_headers()
                self.wfile.write(str.encode(entry.read()))
                entry.close()
                return 
            except:
                print("desio se except")
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
