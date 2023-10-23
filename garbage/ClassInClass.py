

class outerclass(object):
    def __init__(self):
        print('outercalss')
        self._inner = None



    class innerclass():
        def __init__(self):
            print('inner')


        def funcIn(self):
            print('funcIn')

    def init(self):
        print('init')
        self._inner = self.innerclass()

    def funcOut(self):
        self._inner.funcIn()



if __name__ == '__main__':
    x = outerclass()
    x.init()
    x.funcOut()
    x.innerclass().funcIn()
