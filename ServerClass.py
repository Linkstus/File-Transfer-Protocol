import socket
import getpass as pas
import os
import threading
from cryptography.fernet import Fernet
import gzip

#CRC helped with https://www.geeksforgeeks.org/cyclic-redundancy-check-python/

class Server(threading.Thread):

    client = ""
    clientName = ""
    documents = []
    directory = []
    dire = []
    
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.key = self.openKeyFile()
        
        self.functions = {"cd": self.changeDirectory, "put": self.fileIssue,
                          "ls": self.listDirectoryTogether, "get":self.fileTransferFromServer,
                          "decrypt": self.decryptFile, "dir": self.directories,
                          "decompress": self.decompress, "quit": quit}
        
        self.Fer = Fernet(self.key.decode())
        self.serverSocket = socket.socket()
        self.connect()

    def recieveMessages(self):
        self.sendMessages("Welcome how may I serve you: ")
        while True:
            
            message = self.client.recv(1024).decode()

            function, message = self.stringProcess(message)
            
            if(function == "quit"):
                self.functions[function]
            if(function in self.functions):
                self.functions[function](message)
            else:
                self.sendMessages("I'm sorry that is not a command I recongize "
                                      "yet")
            
            
    def connect(self):
        self.serverSocket.bind(("", 65535))
        ls = os.listdir(os.getcwd())
        for i in ls:
            if(os.path.isfile(i)):
                self.documents.append(i)
            else:
                self.directory.append(i)
        print("Server is ready!")
        self.serverSocket.listen(2)
        self.client, clientAddress = self.serverSocket.accept()
        
        self.login()
    
    def openKeyFile(self):
        tempFile = open("yek.key", "rb")
        key = tempFile.read()
        tempFile.close()
        return key

    def sendMessages(self, message):
        self.client.send("Server: {}".format(message).encode())

    def login(self):
        self.clientName = self.client.recv(1024).decode()
        password = self.client.recv(1024).decode()

        if(self.checkPassword(password)):
            passed = self.credintials(password)

            while passed != True:
                self.client.send("password is incorrect please try again: ".encode())
                passed = self.credintials(self.client.recv(1024).decode())
            self.client.send("passed".encode())
        else:
            self.client.send("I'm sorry that password is not valid".encode())

    def checkPassword(self, password):
        password = password.lower()
        
        specialCharacters = (".", "_", "-", "+", '"', "(", ")", ",", ":", ";",
                             "<", ">", "@", "[", "]", "\\")
        if(password.find("@") == -1):
           return False
        person = password[:password.find("@")]

        password = password[password.find("@"):]

        if(len(person) > 64 or person[0] in specialCharacters or person[-1] in specialCharacters):
            return False

        extenstion = ""
        
        for i in range(1, 5):
            extenstion += password[-i]

        if(extenstion[-1] != "."):
            return False

        DomainName = password[1:password.find(extenstion)]

        if(len(DomainName) > 253):
            return False

        return True

    def credintials(self, password):
        self.createLoginFile()

        loginFile = open("login.txt", "r+")

        return (self.createData(loginFile, password) if self.isNewLoginFile()
                    else self.checkInfo(loginFile, password))

    def createLoginFile(self):
        if(os.path.exists("./login.txt") == False):
            open("login.txt", "a").close

    def isNewLoginFile(self):
        if(os.stat("login.txt").st_size == 0):
            return True
        else:
            return False
            
    def createData(self, file, password):
            file.write("{}:{}\n".format(self.clientName, password))
            file.close()
            return True

    def checkInfo(self, file, password):
            lines = file.readlines()
            credintials = {}

            for line in lines:
                tempLines = []
                for word in line.split(":"):
                    if(word.find("\n") > -1):
                        word = word[:len(word) - 1]
                    tempLines.append(word)
                credintials.update({tempLines[0]:tempLines[1]})

            if(self.clientName in credintials.keys()):
                if(credintials[self.clientName] == password):
                    file.close()
                    return True
                else:
                    file.close()
                    return False
            else:
                self.createData(file, password)
                return True

    def stringProcess(self, messages):
        function = ""
        message = ""

        index = 0

        for i in range(0, len(messages)):
            
            if(messages[i] == " "):
                continue
            function += messages[i]
            if(function in self.functions):
                messages = messages[i + 1:]
                break
        
        if(" " in message):
            messages = messages[messages.find(" ") + 1:]

        if(messages.find(" ") == 0):
            messages = messages[1:]

        return (function, messages)

    def changeDirectory(self, message):
        try:
            os.chdir(message)
            del self.dire [:]
            ls = os.listdir(os.getcwd())
            for i in ls:
                if(os.path.isfile(i)):
                    self.documents.append(i)
                else:
                    self.directory.append(i)
            self.sendMessages(os.getcwd())
        except NotADirectoryError as error:
            self.sendMessages("I'm sorry {} is not a directory". format(self.clientName))
            return

    def listDirectoryTogether(self, message):
        self.sendMessages(os.listdir())

    def directories(self, message):
        for i in range(1, len(self.directory)):
            temp = self.directory[i]
            j = i - 1
            while j > -1 and self.directory[j] > temp:
                self.directory[j + 1] = self.directory[j]
                j = j - 1
            self.directory[j + 1] = temp
            
        for i in range(1, len(self.documents)):
            temp = self.documents[i]
            j = i - 1
            while j > -1 and self.documents[j] > temp:
                self.documents[j + 1] = self.documents[j]
                j = j - 1
            self.documents[j + 1] = temp
        
        for i in self.directory:
            self.dire.append(i)
        del self.directory [:]
        
        for i in self.documents:
            self.dire.append(i)
            
        del self.documents [:]
            
        i = 1
        temp = self.dire[0]

        while i < len(self.dire) - 1:
            i += 1
            self.client.send(temp.encode())
            if(self.client.recv(1024).decode() == "got"):
                temp = self.dire[i]
                
            
        self.client.send(self.dire[len(self.dire) - 1].encode())
        self.client.send("finished".encode())
        self.client.recv(1024)

    #put
    def fileIssue(self, fileName):
        self.client.send("Do you want to encrypt, compress, or normal: ".encode())
        question = self.client.recv(1024).decode()

        if question.lower() == "normal":
            self.filePut(fileName)
        if question.lower() == "encrypt":
            self.filePutEncryption(fileName)
        if question.lower() == "compress":
            self.filePutCompress(fileName)

    def filePut(self, fileName):
        fileName = os.getcwd() + "\\" + fileName
        with open(fileName, "wb") as file:

            line = self.client.recv(1024)
            while line != b"Finished":
                file.write(line)
                self.client.send("got".encode())
                line = self.client.recv(1024)
##            line = self.client.recv(1024)
##            while line != b"Finished":
##                crc = self.client.recv(1024)
##                boolean = CRCDecode(crc)
##                tempLine = helper(boolean, line)
##                if():
##                    file.write(line)
##                    self.client.send("got".encode())
##                    line = self.client.recv(1024)
        print("finished")



    def helper(self, boolean, line):
        tempLine = ""
        if(boolean == True):
            if(line == tempLine):
                return line
            else:
                return tempLine
        #self.client.send("got".encode())
        else:
            self.client.send("Resend".encode())
            tempLine, crc = self.client.recv(1024)
            helper(CRCDecode(crc), tempLine)
                    
        
    #file put encryption
    def filePutEncryption(self, fileName):
        file = fileName[:fileName.find(".")]
        extenstion = fileName[fileName.find("."):]
        file = file + "-encrypted"
        fileName = os.getcwd() + "\\" + file + extenstion

        with open(fileName, "wb") as file:

            line = self.client.recv(1024)
            while line != "Finished":
                file.write(line)
                self.client.send("got".encode())
                line = self.client.recv(1024).decode()
                if(line != "Finished"):
                    line = line.encode()

        print("finished")

    def filePutCompress(self, fileName):
        fileName = os.getcwd() + "\\" + fileName + ".gz"
        with gzip.open(fileName, "wb") as file:

            line = self.client.recv(1024)
            while line != b"Finished":
                file.write(line)
                self.client.send("got".encode())
                line = self.client.recv(1024)
        print("finished")

    def decompress(self, fileName):
        realFile = fileName
        if(fileName.find(".gz") < 0):
            self.client.send("error! file is not a decrypt file".encode())
        else:
            file = fileName[:fileName.find(".")]
            extenstion = fileName[fileName.find("."):fileName.find(".", fileName.find(".") + 1)]
            fileName = os.getcwd() + "\\" +  file + extenstion

            with gzip.open(realFile, "rb") as readFile:
                with open(fileName, "wb") as writeFile:
                    line = readFile.read()
                    writeFile.write(gzip.decompress(line))
                    
            self.client.send("Finished".encode())
        print("finished")
        
    #get                      
    def fileTransferFromServer(self, fileName):
        fileName = os.getcwd() + "\\" + fileName

        with open(fileName, "rb") as file:
            line = file.read(1024)

            while line:
                self.client.send(line)
                if(self.client.recv(1024).decode() == "got"):
                   line = file.read(1024)

            self.client.send("Finished".encode())

        print("finished")

    def decryptFile(self, fileName):
        realFile = fileName
        if(fileName.find("-encrypted") < 0):
            self.client.send("error! file is not a encrypted file".encode())
        else:
            file = fileName[:fileName.find("-")]
            extenstion = fileName[fileName.find("."):]
            fileName = os.getcwd() + "\\" +  file + extenstion

            with open(realFile, "rb") as readFile:
                with open(fileName, "wb+") as writeFile:
                    line = readFile.read()
                    line = self.Fer.decrypt(line)
                    writeFile.write(line)


            self.client.send("Finished".encode())
        print("finished")

##    def caeserCypherDecrypt(self, line):
##        line = str(line)
##        code = 5
##        newLine = ""
##        specialCharacters = [" ", "\n", "\r"]
##
##        for i in range(0, len(line)):
##            letter = line[i]
##            if(letter in specialCharacters):
##                if(letter == " "):
##                    newLine += " "
##                elif(letter == "\n"):
##                    newLine += "\n"
##                elif(letter == "\r"):
##                    newLine += "\r"
##                    
##            elif(letter.isupper()):
##                newLine += chr((ord(letter) - code - 65) % 26 + 65)
##            else:
##                newLine += chr((ord(letter) - code - 97) % 26 + 97)
##
##        return newLine

    def CRCEncode(self, line):
        tempLine = ""
        for x in range(0, len(line)):
            tempLine += b"" + ord(line[x])
            
        line = tempLine
            
        appendLine = line + b"000"
        code = "1101"

        leftover = remainder(appendLine, code)

        line += leftover

        return line
        
    def remainder(self, line, code):
        newWord = line[0:len(code)]
        i = len(line)
        
        while i < len(line):

            if(newWord[0] == "1"):
               newWord += self.XoR(code, line[i:len(code) + 1])
            else:
               newWord += self.XoR(code, "000" + line[len(code) + 1])
            i += 1

        if(newWord[0] == "1"):
           newWord += self.XoR(code, newWord)
        else:
           newWord += self.XoR("000", newWord)

        return newWord

    def XoR(self, key, line):
        bits = ""
        for i in range(0, len(line)):
            if(line[i] == key[i]):
                bits += "0"
                continue
            else:
                bits += "1"

        return bits

    def CRCDecode(self, line):
        newWord = line[0:len(line)]
        i = len(line)
        code = "1101"

        appendLine = bytes(line) + b"000"

        leftover = remainder(self, appendLine, code)

        return leftover


            

def main():
    server = Server()
    server.recieveMessages()
##    server.start()
##
##    while True:
##        doSomething = ""

main()
