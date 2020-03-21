from configparser import ConfigParser
import os
import logging

log = logging.getLogger(__name__)

class ConfigChecker():

    def __init__(self):
        self.expectations = []
        self.configObject = ConfigParser()
        self.configUpdateAttempted = False

    def setExpectation(self,section,key,dataType,default,message = None):

        if dataType not in [bool,float,str,int]:
            log.warning("Trying to add expection with not allowed data type [{}]. Allowed types = [bool, int, str, float]".format(dataType))
            return False

        if dataType is int and not self._isInteger(default):
            self._logWrongExpectationDataType(section,key,dataType,default);
            return False

        if dataType is float and not self._isFloat(default):
            self._logWrongExpectationDataType(section,key,dataType,default);
            return False

        if dataType is bool and not self._isBoolean(default):
            self._logWrongExpectationDataType(section,key,dataType,default);
            return False

        entryExists,position = self.expectationExistsAtIndex(section,key)
        if entryExists:
            log.warning("Attempting to and entry which already exists. Section: [{}], Key [{}]".format(section,key))
            return False

        newExpection = {
            'section' : section,
            'key' : key,
            'value' : None,
            'dataType' : dataType,
            'default' : default,
            'message' : message,
            }
        self.expectations.append(newExpection)
        log.debug("Added new expectation with Section: [{}], Key [{}], DataType [{}], Default [{}]".format(section,key,dataType,default))
        return True

    def _logWrongExpectationDataType(self,section,key,dataType,default):
        log.warning("Trying to set expectation Section: [{}], Key [{}], Default [{}] with wrong data type. (Type = [{}])".format(section,key,default,dataType))

    def removeExpectation(self,section,key):
        entryExist, position = self.expectationExistsAtIndex(section,key)
        if entryExist:
            log.debug("Removing expectation with Section: [{}], Key [{}]".format(section,key))
            self.expectations.pop(position)
            return True
        else:
            log.warning("Trying to remove expectation which doesn't exist. Section: [{}], Key [{}]".format(section,key))
            return False

    def expectationExistsAtIndex(self,section,key):
        for i,expectation in enumerate(self.expectations):
            if expectation['section'] == section and expectation['key'] == key:
                return True,i
        return False,None

    def getValue(self,section,key):
        entryExists, position = self.expectationExistsAtIndex(section,key)
        if entryExists:
            return self.expectations[position]['value']
        log.warning("Trying to retreive a value for an expectation which doean't exist. Section: [{}], Key [{}]".format(section,key))
        return None

    def setValue(self,section,key,value):
        if not self.configUpdateAttempted:
            log.warning("Change the value of an expection with Section: [{}], Key: [{}], Value: [{}] when target file not set. Call setConfigurationFile first".format(
                section,key,value))
            return False
        entryExists, position = self.expectationExistsAtIndex(section,key)
        if entryExists:
            if self.expectations[position]['dataType'] is int:
                if self._isInteger(value):
                    self._logValueUpdate(section,key,value,position,True)
                    self.expectations[position]['value'] = value
                    return True
                else:
                    self._logValueUpdate(section,key,value,position,False)
                    return False
            elif self.expectations[position]['dataType'] is float:
                if self._isFloat(value):
                    self._logValueUpdate(section,key,value,position,True)
                    self.expectations[position]['value'] = value
                    return True
                else:
                    self._logValueUpdate(section,key,value,position,False)
                    return False
            elif self.expectations[position]['dataType'] is bool:
                if self._isBoolean(value):
                    self._logValueUpdate(section,key,value,position,True)
                    self.expectations[position]['value'] = value
                    return True
                else:
                    self._logValueUpdate(section,key,value,position,False)
                    return False
            else:
                self.expectations[position]['value'] = value
                self._logValueUpdate(section,key,value,position,True)
                return True
        else:
            log.warning("Cannot update the value of Section [{}], Key [{}] to [{}], entry doesn't exists in expectation list".format(section,key,value))
            return False

    def _logValueUpdate(self,section,key,value,position,success):
        if success:
            log.debug("Updated the value of Section [{}], Key [{}], from [{}] to [{}]".format(section,key,self.expectations[position]['value'],value))
        else:
            log.warning("Cannot update the value of Section [{}], Key [{}], from [{}] to [{}], wrong type (type = [{}])".format(section,
                key,self.expectations[position]['value'],value,self.expectations[position]['dataType']))

    def _isInteger(self,value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _isFloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _isBoolean(self,value):
        return type(value) == bool

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
                log.debug("Writing a new configuration file '{}'".format(filename))
        except PermissionError:
            log.warning("Failed writing configuration file '{} (Permission Error)'".format(filename))
            return False
        except OSError:
            log.warning("Failed writing configuration file '{} (OS Error)'".format(filename))
            return False
        return True

    def setConfigurationFile(self,filename):

        if len(self.expectations) == 0:
            log.warning("Trying to open a configuration file '{}' with no expectations set, nothins was loaded".format(filename))
            return False
        try:
            if len(self.configObject.read(filename)) == 0:
                log.warning("Failed to open configuration file '{}'. Using default values for expectations".format(filename))
                self._loadDefaultsWhereNeeded()
                self.configUpdateAttempted = True;
                return False
        except:
            log.warning("Failed to open configuration file '{}'. Using default values for expectations".format(filename))
            self._loadDefaultsWhereNeeded()
            self.configUpdateAttempted = True;
            return False

        log.debug("Loading configuration file {}".format(filename));
        self._parseConfigValues()
        self._loadDefaultsWhereNeeded()
        self.configUpdateAttempted = True;
        return True

    def _loadDefaultsWhereNeeded(self):
        for expectation in self.expectations:
            if expectation['value'] is None:
                log.debug("Section [{}] with key [{}] not found in configuration file, using default value {}".format(expectation['section'],
                    expectation['key'],
                    expectation['default']))
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
            self._logConversionStatus(True,position)
        except:
            self.expectations[position]['value'] = self.expectations[position]['default']
            self._logConversionStatus(False,position)

    def _convertFloat(self,section,key,position):
        try:
            self.expectations[position]['value'] = self.configObject.getfloat(section,key)
            self._logConversionStatus(True,position)
        except:
            self.expectations[position]['value'] = self.expectations[position]['default']
            self._logConversionStatus(False,position)

    def _convertInt(self,section,key,position):
        try:
            self.expectations[position]['value'] = self.configObject.getint(section,key)
            self._logConversionStatus(True,position)
        except:
            self.expectations[position]['value'] = self.expectations[position]['default']
            self._logConversionStatus(False,position)

    def _logConversionStatus(self,sucess,position):
        if sucess:
            log.debug("Updating Section [{}] with key [{}] to value [{}] found in configuration file".format(self.expectations[position]['section'],
                self.expectations[position]['key'],
                self.expectations[position]['value']))
        else:
            log.warning("Section [{}] with key [{}] of configuration file cannot be parsed as [{}], using default value {}".format(self.expectations[position]['section'],
                self.expectations[position]['key'],
                self.expectations[position]['dataType'],
                self.expectations[position]['default']))
