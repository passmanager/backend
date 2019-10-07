from flask import Flask, request, Response
from flask_cors import CORS
import json
import os
from datetime import datetime
import string
import secrets
import hashlib

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

PORT = 8000
numberOfTimesToHash = 512
passwordsDir = "/passwords" + os.sep
archiveDir = "/archive" + os.sep
hashFileName = "/passhash"
userDir = "user/"

salts = dict()
alphabet = string.ascii_letters + string.digits

def checkPassword(user, passwordHash, salt_id):
    #TODO: Check password with salt logic
    passwordHashToCompare = open(userDir + user + hashFileName).readline().strip()
    salt = salts[user][salt_id]
    for _ in range(512):
        passwordHashToCompare = hashlib.sha512((passwordHashToCompare + salt).encode()).hexdigest()
    salts[user].pop(salt_id, None)
    return passwordHash == passwordHashToCompare

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/user/getSalt/<string:user>", methods=['GET'])
def getSalt(user):
    salt_id = ''.join(secrets.choice(alphabet) for i in range(8))
    salt = ''.join(secrets.choice(alphabet) for i in range(8))
    entry = {salt_id: salt}
    if not user in salts:
        salts[user] = dict()
    salts[user].update(entry)
    return Response('{"salt_id": "' + salt_id + '", "salt": "' + salt +'"}', 200)


@app.route("/user/<string:user>", methods=['GET', 'POST', 'DELETE', 'PATCH'])
def getAllPasswords(user):
    try:
        #check if password is good
        passwordHash = request.args.to_dict()['key']
        salt_id = request.args.to_dict()['salt_id']
        if not checkPassword(user, passwordHash, salt_id):
            return Response('{"error": "wrong password"}', status=403)

        if request.method == 'GET':
            files = os.listdir(userDir + user + passwordsDir)
            global json
            files = sorted(files, key=lambda s: s.casefold())
            return json.dumps(files, ensure_ascii=False)

        return Response('{"error": "not implemented"}', status=501)
    except Exception as ex:
        print('get all passwords list')
        print(type(ex).__name__)
        print(ex)
        return 500

@app.route("/user/<string:user>/<string:password>", methods=['GET', 'POST', 'DELETE', 'PATCH'])
def getSinglePassword(user, password):
    try:
        #check if password is good
        passwordHash = request.args.to_dict()['key']
        salt_id = request.args.to_dict()['salt_id']
        if not checkPassword(user, passwordHash, salt_id):
            return Response('{"error": "wrong password"}', status=403)

        username = userDir + user
        #  password = "".join(['⁄' if word == "" else word for word in self.path.split('/')[3:]]) #not forward slash but an unicode char 2044 ⁄, used because forward slash is seperating files
        if (password[-1] == '⁄'):
            password = password[:-1]
        password = password.replace("%20", " ")

        if request.method == 'GET':
            if not os.path.isfile(username + os.sep + passwordsDir + password):
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

        if request.method == 'POST' or request.method == 'PATCH':
            dataToWrite = request.args.to_dict()['entry'].to_dict()
            if not ('usernameSalt' in dataToWrite and 'username' in dataToWrite and 'passwordSalt' in dataToWrite and 'password' in dataToWrite):
                return Response('{"error": "missing some values"}', 400)
            if os.path.isfile(username + os.sep + passwordsDir + password):
                os.rename(username + os.sep + passwordsDir + password, username + os.sep + archiveDir + password + '  ' + str(datetime.now()))
            f = open(username + os.sep + passwordsDir + password)
            f.write(dataToWrite['usernameSalt'])
            f.write(dataToWrite['username'])
            f.write(dataToWrite['passwordSalt'])
            f.write(dataToWrite['password'])
            f.close()
            return Response('{"success": true}', status=201)

        if request.method == 'DELETE':
            if os.path.isfile(username + os.sep + passwordsDir + password):
                os.rename(username + os.sep + passwordsDir + password, username + os.sep + archiveDir + password + '  ' + str(datetime.now()))
            else:
                return Response('{"error": "password not found"}', status=404)

        return Response('{"error": "not implemented"}', status=501)
    except Exception as ex:
        print('get single password')
        print(type(ex).__name__)
        print(ex)
        return Response('{"error": 404}', status=500)

if __name__ == "__main__":
    app.run('0.0.0.0', port=PORT)
