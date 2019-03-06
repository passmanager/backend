import http.server
import socketserver
import re
import os

PORT = 8000

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
                files = os.listdir(self.path[1:] + "passwords/")
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
        self.send_response(404)
        self.send_header('Content-type', "text/html")
        self.end_headers()
        f = open("index.html")
        self.wfile.write(str.encode(f.read()))
        f.close()
        return


handler = MyHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    try:
        print("Serving at port: " + str(PORT))
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")
        httpd.socket.close()
