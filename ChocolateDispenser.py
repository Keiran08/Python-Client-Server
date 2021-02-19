class State:
    CurrentContext = None
    def __init__(self, Context):
        self.CurrentContext = Context
    def trigger(self):
        return True

class StateContext:
    state = None
    CurrentState = None
    availableStates = {}

    def setState(self, newstate):
        try:
            self.CurrentState = self.availableStates[newstate]
            self.state = newstate
            self.CurrentState.trigger()
            return True
        except KeyError:
            return False

    def getStateIndex(self):
        return self.state
class Transition:
    def insertMoney(self, money):
        print ("Error! You cannot insert money!")
        return False
    def makeSelection(self, option):
        print ("Error! You cannot make selection!")
        return False
    def moneyRejected(self):
        print ("Error! You conot reject money!")
        return False
    def addChocolate(self, number):
        print ("Error! You connot add chocolate!")
        return False
    def dispense(self):
        print ("Error! You connot dispense!")
        return False

class Product:
    description = ""
    cost = 0

class Chocolate(Product):
    def __init__(self):
        self.description = "Chocolate"
        self.cost = 50

class OutOfChocolate(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def addChocolate(self, number):
        print ("Number of chocolates added:", number)
        self.CurrentContext.no_of_chocolates = number
        self.CurrentContext.setState("NoCredit")
        return True

    def moneyRejected(self):
        print ("Rejectng money...")
        self.CurrentContext.credit = 0
        self.CurrentContext.setState("OutOfChcolate")
        return True

class NoCredit(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def insertMoney(self, money):
        print ("Number of credits inserted:",money)
        self.CurrentContext.credit = money
        print ("Total now", money)
        self.CurrentContext.setState("HasCredit")
        return True

class HasCredit(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def insertMoney(self, money):
        print ("Number of credits inserted:", money)
        money += self.CurrentContext.credit
        print ("Total now", money)
        self.CurrentContext.credit+=money
        self.CurrentContext.setState("HasCredit")
        return True

    def makeSelection(self, option):
        print ("Selection made")
        self.CurrentContext.DispensedItem = Chocolate()
        self.CurrentContext.setState("DispensesChocolate")

class DispensesChocolate(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def dispense(self):
        if self.CurrentContext.credit >= self.CurrentContext.DispensedItem.cost:
            print ("Dispensing", self.CurrentContext.DispensedItem.description)
            self.CurrentContext.credit -= self.CurrentContext.DispensedItem.cost
        else:
            print ("Error! Not enough money")
            self.CurrentContext.DispensedItem = None
        if self.CurrentContext.credit > 0:
            self.CurrentContext.setState("HasCredit")
        else:
            self.CurrentContext.setState("NoCredit")
        if self.CurrentContext.no_of_chocolates == 0:
            self.CurrentContext.setState("OutOfChocolate")
        return True

class ChocolateDispenser(StateContext, Transition):
    def __init__(self, inventory_count):
        self.DispensedItem = None
        self.no_of_chocolates = 0
        self.credit = 0
        self.availableStates["OutOfChocolate"] = OutOfChocolate(self)
        self.availableStates["NoCredit"] = NoCredit(self)
        self.availableStates["HasCredit"] = HasCredit(self)
        self.availableStates["DispensesChocoalte"] = DispensesChocolate(self)
        self.setState("OutOfChocolate")
        if inventory_count > 0:
            self.addChocolate(inventory_count)

    def insertMoney(self, money):
        return self.CurrentState.insertMoney(money)

    def makeSeletion(self, option):
        return self.CurrentState.makeSelection(option)

    def moneyRejected(self):
        return self.CurrentState.moneyRejected()

    def addChocolate(self, number):
        return self.CurrentState.addChocolate(number)

    def dispense(self):
        return self.CurrentState.dispense()

    def getProduct(self):
        return self.DispensedItem


if __name__ == '__main__':
    MyDispenser = ChocolateDispenser(10)
    MyDispenser.addChocolate(10)
    MyDispenser.insertMoney(10)
    MyDispenser.insertMoney(10)
    MyDispenser.moneyRejected()
    MyDispenser.insertMoney(50)
    MyDispenser.makeSelection(1)
    MyDispenser.dispense()
    MyFood = MyDispenser.getProduct()
    if MyFood is not None:
        print ("Yum yum!")
    else:
        print ("Boo hoo!")

    print (MyDispenser.getStateIndex())