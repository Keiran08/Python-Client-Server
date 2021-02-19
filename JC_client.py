from sys import argv
from time import sleep
import socket

class State:
    state = None # abstract class
    CurrentContext = None
    def __init__(self, Context):
        self.CurrentContext = Context

class StateContext:
    stateIndex = 0
    CurrentState = NoneavailableStates = []
    availableStates = {} 

    def setState(self, newstate):
        self.CurrentState = self.availableStates[newstate]
        self.startIndex = newstate
    
    def getStateIndex(self):
        return self.stateIndex

class Transition:
    def passive_open(self):
        print ("Error!")
        return False

    def syn(self):
        print ("Error!")
        return False

    def ack(self):
        print ("Error!")
        return False

    def rst(self):
        print ("Error!")
        return False

    def syn_ack(self):
        print ("Error!")
        return False

    def close(self):
        print ("Error!")
        return False

    def fin(self):
        print ("Error!")
        return False

    def timeout(self):
        print ("Error!")
        return False

    def active_open(self):
        print ("Error!")
        return False


class Closed(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def close(self):
        # attempt to close the connection, and resets the object
        try:
          self.CurrentContext.socket.close()
          self.CurrentContext.connection_address = 0
        except:
          pass
        return True
    
    def passive_open(self): # server
        self.CurrentContext.listen()
        print ("Tranisition to the listen state")
        self.CurrentContext.setState("LISTEN")
        return True

    def active_open(self): # client
        self.CurrentContext.make_connection()
        self.CurrentContext.socket.send("SYN")
        self.CurrentContext.setState("SYNSENT")
        return True

    def Trigger(self):
        self.CurrentContext.close()
        return True


class Listen(State, Transition): # serrver
    def __init__(self, Context):
        State.__init__(self, Context)

    def syn(self):
      self.CurrentContext.command = self.CurrentContext.connection.recv(1024)
      if self.CurrentContext.command == "SYN":
          self.CurrentContext.connection.send("SYNACK")
          self.CurrentState.setState("SYNRECVD")
      return True
    
    def Trigger(self):
      # do we need a try and catch here
      # should we be doing the recv in the trigger
      self.CurrentContext.syn()
      return True
        

class SynRecvd(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def Trigger(self):

        return True

class SynSent(State, Transition): # server
    def __init__(self, Context):
        State.__init__(self, Context)
    
    def syn_ack(self):
        # send an ack and transition to established state
        # check that SYNACK has been receieved. 
        pass
    
    def rst(self):
        self.CurrentState.setState("CLOSED")
        return True

    def timeout(self):
      pass

    def Trigger(self):
        pass

class Established(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)
  
    def Trigger(self):
        pass

class FinWait_1(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def Trigger(self):
        pass

class FinWait_2(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def Trigger(self):
        pass

class CloseWait(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def Trigger(self):
        pass

class LastAck(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def Trigger(self):
        pass

class TimedWait(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def Trigger(self):
        pass

class TCPIPSimulator(StateContext, Transition):
    
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 5000
        self.availableStates["CLOSED"] = Closed(self)
        self.availableStates["LISTEN"] = Listen(self)
        self.availableStates["SYNRECVD"] = SynRecvd(self)
        self.availableStates["SYNSENT"] = SynSent(self)
        self.availableStates["ESTABLISHED"] = Established(self)
        self.availableStates["FINWAIT-1"] = FinWait_1(self)
        self.availableStates["FINWAIT-2"] = FinWait_2(self)
        self.availableStates["CLOSEDWAIT"] = CloseWait(self)
        self.availableStates["LASTACT"] = LastAck(self)
        self.availableStates["TIMEDWAIT"] = TimedWait(self)
        self.setState("CLOSED")
        self.connection_addr = 0
        self.connection = None
        self.socket = None
        self.command = None
        
    def passive_open(self):
      return self.CurrentState.passive_open() 
   
    def active_open(self):
      return self.CurrentState.active_open()

    def syn(self):
      return self.CurrentState.syn()
    
    def ack(self):
      return self.CurrentState.ack()
    
    def rst(self):
      return self.CurrentState.rst()
    
    def syn_ack(self):
      return self.CurrentState.syn_ack()
    
    def close(self):
      return self.CurrentState.close()
    
    def fin(self):
      return self.CurrentState.fin()
    
    def timeout(self):
      return self.CurrentState.timeout()

    def listen(self):
        ''' this method initiates a listen socket '''
        # server
        self.socket = socket.socket()
        try:
            print ("waiting for a connection")
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            self.connection, self.connection_address = self.socket.accept()
            # connection acceptance
            return True
        except Exception as err: 
            print (err)
            exit()
       
    def make_connection(self):
        # client
        ''' this method initiates an outbound connection '''
        print ("making a connection")
        self.socket = socket.socket()
        try:
            self.socket.connect((self.host, self.port))
            self.connection_address = self.host
            return True
        except Exception as err:
            print (err)
            exit()
    
    def read_commands(self):
        # The client should be able to read commands from a file
        # called client_commands.txt that will be in the same directory
        pass

    def encryption_decryption(self):
        pass

if __name__ == "__main__":
    if len(argv) < 2:
        print ("Error: too few arguments")
        exit()

    TCPIPSimulator = TCPIPSimulator()
    if argv[1] == "server":
        TCPIPSimulator.passive_open()
    else:
        TCPIPSimulator.active_open()