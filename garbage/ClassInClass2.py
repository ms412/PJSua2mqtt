class account:
    def __init__(self):
        self.bank = account.bank()

    class bank:
        def __init__(self):
            self.balance = 100000

        def whitdraw(self, amount):
            self.balance -= amount

        def deposit(self, amount):
            self.balance += amount

    class bank2:
        def __init__(self):
            print('bank2')

    def call(self):
        self.bank.whitdraw(30)

    def init(self):
        account.bank2()
        self.bank2()


a = account()
print (a.bank.balance)
a.bank.whitdraw(20)
print (a.bank.balance)
a.call()
print (a.bank.balance)
a.init()