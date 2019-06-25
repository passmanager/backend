from flask import Flask, request, Response
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

PORT = 8000
passwordsDir = "/passwords" + os.sep
hashFileName = "/passhash"
userDir = "user/"

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/user/<string:user>")
def getAllPasswords(user):
    try:
        #check if password is good
        passwordHash = request.args.to_dict()['key']
        passwordHashToCompare = open(userDir + user + hashFileName).readline().strip()
        if passwordHash != passwordHashToCompare:
            return Response('{"error": "wrong password"}', status=403)

        files = os.listdir(userDir + user + passwordsDir)
        global json
        files = sorted(files, key=lambda s: s.casefold())
        print(json.dumps(files, ensure_ascii=False))
        return json.dumps(files, ensure_ascii=False)
    except Exception as ex:
        print('get all passwords list')
        print(type(ex).__name__)
        print(ex)
        return

@app.route("/user/<string:user>/<string:password>")
def getSinglePassword(user, password):
    try:
        #check if password is good
        passwordHash = request.args.to_dict()['key']
        passwordHashToCompare = open(userDir + user + hashFileName).readline().strip()
        if passwordHash != passwordHashToCompare:
            return Response('{"error": "wrong password"}', status=403)

        username = userDir + user
        #  password = "".join(['⁄' if word == "" else word for word in self.path.split('/')[3:]]) #not forward slash but an unicode char 2044 ⁄, used because forward slash is seperating files
        if (password[-1] == '⁄'):
            password = password[:-1]
        password = password.replace("%20", " ")
        if not os.path.isfile(username + os.sep + passwordsDir + password):
            self.send_error(404, password.replace('⁄', '/') + " not found")
            return Response('{"error": "password not found"}', status=404)
        entry = open(username + os.sep + passwordsDir + password)
        data = entry.read()
        entry.close()
        temp = dict()
        temp['usernameSalt'] = data.split('\n')[0]
        temp['username'] = data.split('\n')[1]
        temp['passwordSalt'] = data.split('\n')[2]
        temp['password'] = data.split('\n')[3]

        return json.dumps(temp)
    except Exception as ex:
        print('get single password')
        print(type(ex).__name__)
        print(ex)
        return '{"error": 404}'

if __name__ == "__main__":
    app.run(port=PORT)
