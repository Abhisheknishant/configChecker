
class ConfigChecker():

    def __init__(self):
        self.expectations = []

    def setExpectation(self,section,key,default,message = None):
        newExpection = {
            'section' : section,
            'key' : key,
            'default' : default,
            'message' : message,
            }
        self.expectations.append(newExpection)


