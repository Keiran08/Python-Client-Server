from State import *

class Transition:
    def _(self, value):
        print ("Error!")
        return False

class Accepting(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

        def _(self, value):
            if value == 1:
                self.CurrentContext.setState("REJECTING")
            else:
                self.CurrentContext.setState("ACCEPTING")
            return True

class Rejecting(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def_(self, value):
    if value == 1:
        self.CurrentContext.setState("ACCEPTING")
    else:
        self.CurrentContext.setState("REJECTING")
    return True

class AENO(StateContext, Transition):
    def __init__(self):
        self.availableStates["ACCEPTING"] = Accepting(self)
        self/availableStates["REJECTING"] = Rejecting(self)
        self.setState("ACCEPTING")

    def _(self, value):
        self.CurrentState._(value)

if __name__ == '__main__':
    zerosones = [1,0,0,1]
    FiniteStateAutomata = AENO()
    for value in zerosones:
        FiniteStateAutomata._(value)
    print(FiniteStateAutomata.getStateIndex())