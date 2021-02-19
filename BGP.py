from State import *
from socket import socket
from sys import argv
from time import sleep

class Transition:
    def idle(self):
        print("Error! Cannot Transition to idle!")
        return False
    def connect(self):
        print("Error! Cannot Transition to connect!")
        return False
    def active(self):
        print("Error! Cannot Transition to active!")
        return False
    def open_sent(self):
        print("Error! Cannot Transition to open sent!")
        return False
    def open_confirm(self):
        print("Error! Cannot Transition to open confirm!")
        return False
    def established(self):
        print("Error! Cannot Transition to established!")
        return False

class Idle(State, Transition):
    '''This is the first stage of the BGP FSM. It either
    tries to initiate a TCP connection to the BGP peer
    (client mode), or listens for a new connect from
    a peer (server mode).'''
    def __init__(self, Context):
        State.__init__(self, Context)
    def idle(self):
        #only called when operating as a server
        #initiate listening process
        #and transition to connect state when connection made
        print("At idle and listening!")
        self.CurrentContext.listen() #server process
        self.CurrentContext.connect()
        return True
    def connect(self):
        #only called when operating as a client
        #initiate connection process
        #and transition to connect state when connection made
        print("Contacting peer...")
        if self.CurrentContext.connection_address == 0: #in client mode
            self.CurrentContext.make_connection()
        print("Connection made!")
        sleep(self.CurrentContext.sleep_time)
        print("Transitioning to connect!")
        self.CurrentContext.setState("CONNECT")
        return True
    def trigger(self):
        #close open socket and reset object
        #return true if succeed. False otherwise
        try:
            self.CurrentContext.socket.close() #attempt to terminate socket
            self.connection_address = 0 #reset address attribute
            print("Closing connection!")
            return True
        except: #no current connection
            return False

class Connect(State, Transition):
    '''The connect state's role is to send out open messages,
    which are used to initiate BGP peer conections. It also
    provides the ability to retry connection attempts that fail
    - i.e. it periodically retry a TCP connection if inital attempts
    fail and times out. This latter functionality hasn't been
    implemented in this model for the sake of simplicity'''
    def __init__(self, Context):
        State.__init__(self, Context)
    def idle(self):
        print("Transitioning to idle!")
        self.CurrentContext.setState("IDLE")
        return True
    def connect(self):
        print("Transitioning to connect!")
        self.CurrentContext.setState("CONNECT")
        return True
    def active(self):
        print("Transitioning to active!")
        self.CurrentContext.setState("ACTIVE")
        return True
    def open_sent(self):
        #send open command via existing connection
        #and transition to open sent state
        print("Sending open command...")
        try:
            self.CurrentContext.connection.send("OPEN".encode()) #server mode if works
        except:
            self.CurrentContext.socket.send("OPEN".encode()) #slient mode otherwise
        print("Transitioning to open sent!")
        self.CurrentContext.setState("OPENSENT")
        return True
    def trigger(self):
        #display address of the connecting system
        #and trigger open_sent method
        print("Connection with: " + str(self.CurrentContext.connection_address))
        return self.CurrentContext.open_sent()

class Active(State, Transition):
    '''The active state implements the "heartbeat"
    functionality - i.e. it periodically checks to
    see if the TCP connection is still alive by
    reconnecting. This functionality hasn't been
    implemented in this model for the sake of simplicity'''
    def __init__(self, Context):
        State.__init__(self, Context)
    def idle(self):
        print("Transitioning to idle!")
        self.CurrentContext.setState("IDLE")
        return True
    def connect(self):
        print("Transitioning to connect!")
        self.CurrentContext.setState("CONNECT")
        return True
    def active(self):
        print("Transitioning to active!")
        self.CurrentContext.setState("ACTIVE")
        return True
    def open_sent(self):
        print("Transitioning to open sent!")
        self.CurrentContext.setState("OPENSENT")
        return True

class OpenSent(State, Transition):
    '''The open sent state role is to receieve open messages
    from BGP peers. it also has the responsibility to verify
    these messages - i.e. it checks to see if the parameters
    of the BGP connection are valid. This latter functionality
    hasn't been implemented in this model for the sake of
    simplicity'''
    def __init__(self, Context):
        State.__init__(self, Context)
    def idle(self):
        print("Transitioning to idle!")
        self.CurrentContext.setState("IDLE")
        return True
    def active(self):
        print("Transitioning to active!")
        self.CurrentContext.setState("ACTIVE")
        return True
    def open_confirm(self):
        #when open command received, transition to open confirm state
        try:
            command = self.CurrentContext.connection.recv(1024) #server mode if works
        except:
            command = self.CurrentContext.socket.recv(1024) #client mode otherwise
        sleep(self.CurrentContext.sleep_time)
        if command.decode() == "OPEN":
            print("Open command received...")
            print("Transitioning to open confirm!")
            self.CurrentContext.setState("OPENCONFIRM")
        else:
            return self.CurrentContext.idle()
        return True
    def trigger(self):
        #display address of system open command was sent to
        #and trigger open_confirm method
        print("Open command sent to " + str(self.CurrentContext.connection_address))
        return self.CurrentContext.open_confirm()

class OpenConfirm(State, Transition):
    '''in the BGP protocol, the open confirm state listens
    out for  Keepalive or Notification messages. Upon receipt
    of a neighbor's Keepalive, the state is moved to Established.
    If a Notification message is received, and the state is moved
    to Idle. This last feature hasn't been implemented in this model
    for the sake of simplicity'''
    def __init__(self, Context):
        State.__init__(self, Context)
    def idle(self):
        print("Transitioning to idle!")
        self.CurrentContext.setState("IDLE")
        return True
    def open_confirm(self):
        print("Transitioning to open confirm!")
        self.CurrentContext.setState("OPENCONFIRM")
        return True
    def established(self):
        #send and receive keepalive messages
        try:
            self.CurrentContext.connection.send("KEEPALIVE".encode())
            command = self.CurrentContext.connection.recv(1024) #server mode if works
        except:
            self.CurrentContext.socket.send("KEEPALIVE".encode())
            command = self.CurrentContext.socket.recv(1024) #client mode otherwise
        sleep(self.CurrentContext.sleep_time)
        if command.decode() == "KEEPALIVE":
            print("Keepalive command received...")
            print("Transitioning to established!")
            self.CurrentContext.setState("ESTABLISHED")
        else:
            return self.CurrentContext.idle()
        return True
    def trigger(self):
        #trigger estabilshed method
        return self.CurrentContext.established()

class Established(State, Transition):
    '''The established state handles the exchange of
    route information. This functionality hasn't
    been implemented in this model for the sake of
    simplicity. The only role the established state
    has in this model is to terminate the demo via
    its trigger method'''
    def __init__(self, Context):
        State.__init__(self, Context)
    def idle(self):
        print("Transitioning to idle!")
        self.CurrentContext.setState("IDLE")
        return True
    def established(self):
        print("Transitioning to open established!")
        self.CurrentContext.setState("ESTABLISHED")
        return True
    def trigger(self):
        #terminate demo by tranistioning to idle
        sleep(self.CurrentContext.sleep_time)
        print("Demo finished!" )#this trigger terminates protocol demo
        sleep(self.CurrentContext.sleep_time)
        return self.CurrentContext.idle()

class BGPPeer(StateContext, Transition):
    def __init__(self):
        self.sleep_time = 2 #puts pauses in script for demo purposes. Set to 0 if not required
        self.host = "127.0.0.1"
        self.port = 5000
        self.connection_address = 0
        self.socket = None
        self.availableStates["IDLE"] = Idle(self)
        self.availableStates["CONNECT"] = Connect(self)
        self.availableStates["ACTIVE"] = Active(self)
        self.availableStates["OPENSENT"] = OpenSent(self)
        self.availableStates["OPENCONFIRM"] = OpenConfirm(self)
        self.availableStates["ESTABLISHED"] = Established(self)
        print("Transitioning to idle!")
        self.setState("IDLE")

    def idle(self):
        return self.CurrentState.idle()
    def connect(self):
        return self.CurrentState.connect()
    def active(self):
        return self.CurrentState.active()
    def open_sent(self):
        return self.CurrentState.open_sent()
    def open_confirm(self):
        return self.CurrentState.open_confirm()
    def established(self):
        return self.CurrentState.established()

    def listen(self):
        '''this method initiates a listen socket'''
        self.socket = socket()
        try:
            self.socket.bind((self.host,self.port))
            self.socket.listen(1)
            self.connection, self.connection_address = self.socket.accept() #connection acceptance
            return True
        except Exception as err:
            print(err)
            exit()

    def make_connection(self):
        '''this method initiates an outbound connection'''
        self.socket = socket()
        try:
            self.socket.connect((self.host, self.port))
            self.connection_address = self.host
        except Exception as err:
            print(err)
            exit()

if __name__ == '__main__':
    if len(argv) < 2:
        argv.append("client")
    
    ActivePeer = BGPPeer()
    if argv[1] == "server":
        print("Running in server mode!")
        ActivePeer.idle()
    else:
        print("Running in client mode!")
        ActivePeer.connect()
