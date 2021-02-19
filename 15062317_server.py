from State import *
from socket import socket
from sys import argv


class StateContext:
    state = None
    CurrentState = None
    stateAvailable = {}

    def setState(self, newState): #Function to change the state of the state machine to the given state name in the parameter
        try:
            self.CurrentState = self.stateAvailable[newState] #Fetch the object of the desired state from the available state dictionary
            self.state = newState 
            self.CurrentState.trigger()
            return True
        except KeyError: 
            return False

    def getStateIndex(self):
        return self.state

class Transitions:
    def Listen(self):
        print("Error!")
        return False
    def Established(self):
        print("Error!")
        return False
    def synRec(self):
        print("Error!")
        return False
    def Closed(self):
        print("Error!")
        return False
    def closedWait(self):
        print("Error!")
        return False
    def lastAck(self):
        print("Error!")
        return False

class Closed(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def Listen(self):
        self.CurrentContext.setState('LISTEN')
    def trigger(self):
        try:
            self.CurrentContext.socket.close()
            self.CurrentContext.connection_address = 0
            print("Terminating connection")
            self.CurrentContext.Listen()
            return True
        except:
            return False

class Listen(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def trigger(self):
        print("Attempting a new connection")
        self.CurrentContext.socket = socket()
        try:
            self.CurrentContext.socket.bind((self.CurrentContext.host, self.CurrentContext.port))
            self.CurrentContext.socket.Listen(1)
            self.CurrentContext.connection, self.CurrentContext.connection_address = self.CurrentContext.socket.accept()
            self.synAck()
            return True
        except Exception as err:
            print(err)
            exit()
    def synRec(self):
        self.CurrentContext.setState("Syn received")

class closedWait(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def trigger(self):
        print("[ClosedWait]")
        print("Ending connection")
        self.CurrentContext.connection.send("Ack".encode())
        inbound = self.CurrentContext.connection.recv(1024)
        if inbound.decode() == "Finished":
            print(inbound.decode() + "Recieved")
            self.CurrentContext.lastAck()
            return True
        else:
            return False
    def lastAck(self):
        self.CurrentContext.setState("LastAck")

class synRec(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def trigger(self):
        print("[SynRecieved]")
        self.CurrentContext.connection.send("Syn+Ack".encode())
        inbound = self.CurrentContext.connection.recv(1024)
        if inbound.decode() == "Ack":
            print(inbound.decode() + "Recieved")
            self.CurrentContext.Established()
            return True
        else:
            return False
    def Established(self):
        self.CurrentContext.setState("Established")


class Established(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def closedWait(self):
        self.CurrentContext.setState("ClosedWait")
    def trigger(self):
        print("Established")
        print("Connection has been Establisheded")
        while True:
            textToClient = input("Please enter your data:")
            self.CurrentContext.connection.send(textToClient.encode())
            inbound = self.CurrentContext.connection.recv(1024)
            if inbound.decode() == "Finished":
                print(inbound.decode() + "Recieved")
                self.CurrentContext.closedWait()
                return True
            else:
                print("The clients response is: ", inbound.decode())


class lastAck(State, Transitions):
    def __init__(self,Context):
        State.__init__(self,Context)
    def trigger(self):
        self.CurrentContext.connection.send("Finished".encode())
        inbound = self.CurrentContext.connection.recv(1824)
        if inbound.decode() == "ACK":
            self.CurrentContext.Closed()
            return True
        else:
            return False
    def Closed(self):
        self.CurrentContext.setState("Closed")

class TCPServer (StateContext, Transitions):
    def __init__(self):
        self.host = "" #Variable to hold the desired address to bind to the socket
        self.port = 5001
        self.connection_address = 0
        self.socket = None
        self.stateAvailable["Closed"] = Closed(self)
        self.stateAvailable["Listen"] = Listen(self)
        self.stateAvailable["Syn-Recieved"] = synRec(self)
        self.stateAvailable["Establisheded"] = Established(self)
        self.stateAvailable["closeWait"] = closedWait(self)
        self.stateAvailable["lastAck"] = lastAck(self)
        self.setState("Closed")

    def Closed(self):
        return self.CurrentState.Closed()
    def Listen(self):
        return self.CurrentState.Listen()
    def synRec(self):
        return self.CurrentState.synRec()
    def Established(self):
        return self.CurrentState.Established()
    def lastAck(self):
        return self.CurrentState.lastAck()
    def closedWait(self):
        return self.CurrentState.closedWait()

if __name__ == "__main__":
    server = TCPServer()
    server.Listen()