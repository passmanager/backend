from flask import Flask, request, Response
from flask_cors import CORS
import json
import os
from datetime import datetime
import string
import secrets
import hashlib
import sqlite3

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

PORT = 8000
numberOfTimesToHash = 512
passwordsDir = "/passwords" + os.sep
databaseName = "/passwords.db"
archiveDir = "/archive" + os.sep
hashFileName = "/passhash"
userDir = "user/"

ENTRY_TABLE = "ENTRY"
URL_TABLE = "URL_TABLE"
PACKAGE_TABLE = "PACKAGE_TABLE"

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

def createDatabase(user):
    db = sqlite3.connect(userDir + user + databaseName)
    db.execute("CREATE TABLE IF NOT EXISTS " + ENTRY_TABLE + " ( id INTEGER primary key AUTOINCREMENT, name TEXT unique, usernameSalt TEXT, username TEXT, passwordSalt TEXT, password TEXT, lastModified datetime);");
    db.execute("CREATE TABLE IF NOT EXISTS " + URL_TABLE + " ( entryId INTEGER, url TEXT, lastModified datetime);");
    db.execute("CREATE TABLE IF NOT EXISTS " + PACKAGE_TABLE + " (entryId INTEGER, packageName TEXT, lastModified datetime);");
    db.commit()

def readAllFromTable(user, tableName):
    db = sqlite3.connect(userDir + user + databaseName)
    res = db.execute("SELECT * FROM " + tableName + ";")
    array = [i for i in res]
    db.close()
    return array

def getEntryNamesFromDatabase(user):
    db = sqlite3.connect(userDir + user + databaseName)
    res = db.execute("SELECT name FROM " + ENTRY_TABLE + ";" )
    array = [i[0] for i in res]
    db.close()
    return array

def getPasswordByName(user, name):
    db = sqlite3.connect(userDir + user + databaseName)
    res = db.execute("SELECT * FROM " + ENTRY_TABLE + " where name = ?", [name])
    array = [i for i in res]
    db.close()
    if len(array) == 0:
        return False
    passwordTuple = array[0]
    temp = dict()
    temp["id"] = passwordTuple[0]
    temp["name"] = passwordTuple[1]
    temp["usernameSalt"] = passwordTuple[2]
    temp["username"] = passwordTuple[3]
    temp["passwordSalt"] = passwordTuple[4]
    temp["password"] = passwordTuple[5]
    try:
        temp["lastModified"] = passwordTuple[6]
    except:
        pass
    return temp

def insertPassword(user, data):
    if not 'lastModified' in data or data['lastModified'] == None:
        data['lastModified'] = datetime.utcnow()
    db = sqlite3.connect(userDir + user + databaseName)
    res = db.execute("INSERT INTO " + ENTRY_TABLE + " (id, name, usernameSalt, username, passwordSalt, password, lastModified) values (?, ?, ?, ?, ?, ?, ?)", [data['id'], data['name'], data['usernameSalt'], data["username"], data['passwordSalt'], data['password'], data['lastModified']])
    db.commit()
    db.close()


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
            entries = getEntryNamesFromDatabase(user)
            global json
            entries = sorted(entries, key=lambda s: s.casefold())
            return json.dumps(entries, ensure_ascii=False)

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
            temp = getPasswordByName(user, password)
            if temp == False:
                return Response('{"error": "not found"}', 404)
            return json.dumps(temp)

        if request.method == 'POST' or request.method == 'PATCH':
            dataToWrite = request.args.to_dict()['entry'].to_dict()
            if not ('usernameSalt' in dataToWrite and 'username' in dataToWrite and 'passwordSalt' in dataToWrite and 'password' in dataToWrite):
                return Response('{"error": "missing some values"}', 400)
            if not ('id' in dataToWrite):
                dataToWrite['id'] = None
            insertPassword(user, dataToWrite)
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
