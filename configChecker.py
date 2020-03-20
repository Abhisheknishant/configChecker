from configparser import ConfigParser
import os

class ConfigChecker(ConfigParser):

    def __init__(self):
        self.expectations = []
        self.configObject = ConfigParser()

    def setExpectation(self,section,key,dataType,default,message = None):

        # Check types here

        entryExists,position = self.expectationExistsAtIndex(section,key)
        if entryExists:
            return

        newExpection = {
            'section' : section,
            'key' : key,
            'value' : None,
            'dataType' : dataType,
            'default' : default,
            'message' : message,
            }
        self.expectations.append(newExpection)

    def removeExpectation(self,section,key):
        entryExist, position = self.expectationExistsAtIndex(section,key)
        if entryExist:
            self.expectations.pop(position)

    def expectationExistsAtIndex(self,section,key):
        for i,expectation in enumerate(self.expectations):
            if expectation['section'] == section and expectation['key'] == key:
                return True,i
        return False,None

    def getValue(self,section,key):
        entryExists, position = self.expectationExistsAtIndex(section,key)
        if entryExists:
            return self.expectations[position]['value']
        return None

    def printExpectations(self):
        print("Configuration Values")
        for expectation in self.expectations:
            print()
            print("Section:\t",expectation['section'])
            print("Key\t\t",expectation['key'])
            print("Data Type:\t",expectation['dataType'])
            print("Value:\t\t",expectation['value'])
            print("Default Value:\t",expectation['default'])

    def writeConfiguration(self,filename):

        if len(self.expectations) == 0:
            return False

        newConfig = ConfigParser();

        for expectation in self.expectations:
            if not newConfig.has_section(expectation['section']):
                newConfig.add_section(expectation['section'])
            newConfig[expectation['section']][expectation['key']] = str(expectation['value'])
        try:
            with open(filename,'w') as f:
                newConfig.write(f)
        except PermissionError:
            return False
        except OSError:
            return False
        return True

    def setConfigurationFile(self,filename):

        if len(self.expectations) == 0:
            return False
        try:
            if len(self.configObject.read(filename)) == 0:
                self._loadDefaultsWhereNeeded()
                return False
        except:
            self._loadDefaultsWhereNeeded()
            return False

        self._parseConfigValues()
        self._loadDefaultsWhereNeeded()
        return True

    def _loadDefaultsWhereNeeded(self):
        for expectation in self.expectations:
            if expectation['value'] is None:
                expectation['value'] = expectation['default']

    def _parseConfigValues(self):
        for section in self.configObject.sections():
            for key in self.configObject[section]:
                entryExists,position = self.expectationExistsAtIndex(section,key)
                if(entryExists):
                    dataType = self.expectations[position]['dataType']
                    if dataType is int:
                        self._convertInt(section,key,position)
                    elif dataType is bool:
                        self._convertBoolean(section,key,position)
                    elif dataType is float:
                        self._convertFloat(section,key,position)
                    else:
                        self.expectations[position]['value'] = self.configObject.get(section,key)

    def _convertBoolean(self,section,key,position):
        try:
            self.expectations[position]['value'] = self.configObject.getboolean(section,key)
        except:
            self.expectations[position]['value'] = self.expectations[position]['default']

    def _convertFloat(self,section,key,position):
        try:
            self.expectations[position]['value'] = self.configObject.getfloat(section,key)
        except:
            self.expectations[position]['value'] = self.expectations[position]['default']

    def _convertInt(self,section,key,position):
        try:
            self.expectations[position]['value'] = self.configObject.getint(section,key)
        except:
            self.expectations[position]['value'] = self.expectations[position]['default']
