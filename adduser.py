from os import mkdir, mknod, path
from hashlib import sha512

username = input("Username:")
password = sha512(input("Password:").encode()).hexdigest()

file_location = path.dirname(path.abspath(__file__))

if not path.isdir(file_location+"/user"):
	mkdir(file_location+"/user")


user_location  = file_location+"/user/"+username

if not path.isdir(user_location):
	mkdir(user_location)


with open(user_location+"/passhash", "w+") as file:
	file.truncate()
	file.write(password)


if not path.isdir(user_location+"/passwords"):
	mkdir(user_location+"/passwords")