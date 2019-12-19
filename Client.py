#caeser cipher code helped from geeksforgeeks

#client

import socket
from cryptography.fernet import Fernet
import getpass as pas
import math
import os
import time

userName = pas.getuser()

def login():
    
    clientSocket.send(userName.encode())
    clientSocket.send(pas.getpass().encode())
    credintials()


def credintials():
    message = ""

    while message != "passed":
        message = clientSocket.recv(1024).decode()
        if(message != "passed"):
            clientSocket.send(pas.getpass().encode())
        

def communication():
    
    function = ""
    
    while function.lower() != "quit":
        function = input(">>> ")
        clientSocket.send(function.encode())
        if(function.find("cd") > -1):
            changeDirectory()
        if(function.find("ls") > -1):
            listDirectoryTogether()
        if(function.find("put") > -1):
            fileHelper(function)
        if(function.find("decrypt") > -1):
            fileDecrypt()
        

            
##        if(function.find("get") > -1):
##            fileTransferFromServer(function)

        #print(clientSocket.recv(1024).decode())

def changeDirectory():
    print(clientSocket.recv(1024).decode())
    
def listDirectoryTogether():
    directories = clientSocket.recv(1024).decode()
    directories = directories.split(", ")

    lenOfList = len(directories)/2

    if(abs(lenOfList) % 2 != 0): lenOfList = math.floor(lenOfList) + 1

    for lists in directories:
        print(lists)


##    position = 0
##
##    for i in range(0, lenOfList):
##        for j in range(0, 3):
##            print("{}\t".format(directories[position]))
##            position += 1

def fileHelper(function):
    print(clientSocket.recv(1024).decode())
    user = input(">>> ")

    files = function[4:]
    
    if user == "normal":
        clientSocket.send("normal".encode())
        fileTransfertoServer(files)
    if user == "encrypt":
        clientSocket.send("encrypt".encode())
        fileTransfertoServerEncryption(files)
##    if user == "compress":
##        clientSocket.send("compress".encode())
##        fileTransfertoServerCompress(files)


#standard put
def fileTransfertoServer(files):
    
    with open(files, "rb") as file:

        line = file.read(1024)
        
        while line:
            clientSocket.send(line)
            server = clientSocket.recv(1024).decode()
            if(server.find("got") >= 0):
                line = file.read(1024)

        clientSocket.send("Finished".encode())
        print("Finished")
            

#encrypted put
def fileTransfertoServerEncryption(files):
    with open(files, "rb") as file:

        line = file.read(1024)
        line = Fer.encrypt(line)
        
        
        while line:
            clientSocket.send(line)
            if(clientSocket.recv(1024).decode() == "got"):
                line = file.read(1024)
                if(line == b""):
                    break
                line = Fer.encrypt(b"" + line)
                
                

        clientSocket.send("Finished".encode())
        print("Finished")

def fileTransferfromServer(files):
    files = files[4:]

    with open(files, "wb") as file:
        line = clientSocket.recv(1024)

        while line != b"Finished":
            file.write(line)
            clientSocket.send("got".encode())
            line = clientSocket.recv(1024)

    print("finished")

##def caeserCypherEncrypt(words):
##    words = str(words)
##    code = 5
##    newWord = ""
##    specialCharacters = [" ", "\n", "\r"]
##
##    """E_n(x) = (x + n) % 26"""
##    
##    for i in range(0, len(words)):
##        letter = words[i]
##        if(letter in specialCharacters):
##            if(letter == " "):
##                newWord += " "
##            elif(letter == "\n"):
##                newWord += "\n"
##            elif(letter == "\r"):
##                newWord += "\r"
##                    
##        elif(letter.isupper()):
##            newWord += chr((ord(letter) + code - 65) % 26 + 65)
##        else:
##            newWord += chr((ord(letter) + code - 97) % 26 + 97)
##
##    return newWord
        
def fileTransfertoServerCompress(files):
    with open(files, "rb") as file:

        line = file.read(1024)
        
        while line:
            clientSocket.send(line)
            server = clientSocket.recv(1024).decode()
            if(server.find("got") >= 0):
                line = file.read(1024)

        clientSocket.send("Finished".encode())
        print("Finished")

def fileTransferFromServer(function):
    files = function[:4]

    with open(files, "wb") as file:
        line = clientSocket.recv(1024)
        while line != b"Finished":
            file.write(line)
            self.clientSocket.send("got".encode())
            line = clientSocket.recv(1024)

    print("finished")

def fileDecrypt():
    print(clientSocket.recv(1024).decode())

def main():
    global clientSocket
    global userName
    global Fer

    with open("yek.key", "rb") as file:
        key = file.read()
        Fer = Fernet(key.decode())
    
    clientSocket = socket.socket()

##    IPAddress = input("What is the IP Adress you are looking for: ")
##    port = int(input("Port: "))
    IPAddress = "192.168.65.97"
    port = 65535

    clientSocket.connect((IPAddress, port))

    #login()

    print(clientSocket.recv(1024).decode())

    communication()
    
    

main()
    
