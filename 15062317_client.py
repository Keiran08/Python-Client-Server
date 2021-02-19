from State import *
from socket import socket
from sys import argv

class StateContext:
    state = None #Variable to hold the dictionary key of the current state
    CurrentState = None
    availableStates = {} #Dictionary of available states

    def setState(self, newState):
        try:
            self.CurrentState = self.availableStates[newState]
            self.state = newState
            self.CurrentState.trigger()
            return True
        except KeyError:
            return False

    def getStateIndex(self):
        return self.state

class Transitions:
    def Closed(self):
        print("Error!")
        return False
    def synSent(self):
        print("Error!")
        return False
    def Established(self):
        print("Error!")
        return False
    def finWait1(self):
        print("Error!")
        return False
    def finWait2(self):
        print("Error!")
        return False
    def timedWait(self):
        print("Error!")
        return False

class synSent(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def RST(self):
        print("Resetting")
        self.CurrentContext.setState("Closed")
    def TimeOut(self):
        print("Resetting")
        self.CurrentContext.setState("Closed")
    def Established(self):
        print("Resetting")
        self.CurrentContext.setState("Established")
    def trigger(self):
        print("[SynSent]")
        print("Trying new connection")
        try:
            self.CurrentContext.socket = socket()
            self.CurrentContext.socket.connect((self.CurrentContext.host, self.CurrentContext.port))
            self.CurrentContext.connection_address = self.CurrentContext.host
            self.CurrentContext.socket.send("Syn".encode())
            inbound = self.CurrentContext.socket.recv(1824)
            if inbound.decode() == "Syn+Ack":
                self.CurrentContext.Established()
                return True
            elif inbound.decode() != "Syn+Ack":
                self.CurrentContext.RST()
                return True
            else:
                self.CurrentContext.TimeOut()
                return False
        except:
            return False

class Closed(State, Transitions):
    def __init__(self, Context): #Constructor to call the superclasses constructor
        State.__init__(self, Context)
    def synSent(self):
        self.CurrentContext.setState("syn_Sent")
    def trigger(self): #States's trigger function to run as soon as the state is changed
        try:
            self.CurrentContext.socket.close()
            self.CurrentContext.connection_address = 0
            print("[Closed]")
            print_("Connection End")
            return True
        except:
            return False

class Established(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def finWait1(self):
        self.CurrentContext.setState("Finished wait")
    def trigger(self):
        self.CurrentContext.socket.send("Ack".encode())
        print("[Established]")
        print("Connection has been Establisheded")
        while True:
            inbound = self.CurrentContext.socket.recv(1824)
            print_("The server has stated: ", inbound.decode())
            textToServer = input("Please enter your data:")
            if textToServer == "Finished":
                self.CurrentContext.socket.send(textToServer.encode())
                self.CurrentContext.finWait1()
                return True
            self.CurrentContext.socket.send(textToServer.encode())

class finWait1(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def finWait2(self):
        self.CurrentContext.setState("Finished Wait")
        def trigger(self):
            print("[Finished Wait 2]")
            print("Attempting to connect to the server")
            self.CurrentContext.socket.send("Finished".encode())
            inbound = self.CurrentContext.socket.recv(1824)
            if inbound.decode() == "Finished":
                self.CurrentContext.finWait2()
                return True
            else:
                return False

class finWait2(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def timedWait(self):
        self.CurrentContext.setState("Timed Wait")
    def trigger(self):
        print("[Finished Wait 2")
        inbound = self.CurrentContext.socket.recv(1824)
        if inbound.encode() == "Finished":
            self.CurrentContext.timedWait()
            return True
        else:
            return False

class timedWait(State, Transitions):
    def __init__(self, Context):
        State.__init__(self, Context)
    def Closed(self):
        self.CurrentContext.setState("Closed") #Transition to the closed state
    def trigger(self):
        print("[Timed Wait]")
        self.CurrentContext.socket.send("Ack".encode())
        self.CurrentContext.Closed()

class TCPSimulator(StateContext, Transitions):
    def __init__(self):
        self.host = "127.0.0.1" #Variable to hold the desired address to connect to
        self.port = 5001
        self.connection_address = 0 #Variable to hold the address of the server connected to
        self.socket = None #Variable to hold the socket object
        self.availableStates["Closed"] = Closed(self)
        self.availableStates["SynSent"] = synSent(self)
        self.availableStates["Established"] = Established(self)
        self.availableStates["finWait1"] = finWait1(self)
        self.availableStates["finWait2"] = finWait2(self)
        self.availableStates["timedWait"] = timedWait(self)
        self.setState("Closed")

#Functions to call the transition functions for the state that the machine is current in
    def Closed(self):
        return self.CurrentState.Closed()

    def synSent(self):
        return self.CurrentState.synSent()

    def Established(self):
        return self.CurrentState.Established()

    def finWait1(self):
        return self.CurrentState.finWait1()

    def finWait2(self):
        return self.CurrentState.finWait2()

    def timedWait(self):
        return self.CurrentState.timedWait()

    def RST(self):
        return self.CurrentState.RST()

    def TimeOut(self):
        return self.CurrentState.TimeOut()

if __name__ == "__main__":
    if len(argv) < 2:
        print ("Error: too few arguments")
        exit()

    TCPSimulator = TCPSimulator()
    if argv[1] == "server":
        TCPSimulator.passive_open()
    else:
        TCPSimulator.active_open()