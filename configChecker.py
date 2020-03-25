from configparser import ConfigParser
import os
import logging

log = logging.getLogger(__name__)

class ConfigChecker():

    def __init__(self):
        self.__expectations = []
        self.__configObject = ConfigParser()
        self.__configReady = False
        self.__configurationFile = None

    def getExpectations(self):
        return self.__expectations

    def getConfigParserObject(self):
        return self.__configObject

    def setExpectation(self,section,key,dataType,default,message = None):

        if dataType not in [bool,float,str,int]:
            log.warning("Trying to add expection with not allowed data type [{}]. Allowed types = [bool, int, str, float]".format(dataType))
            return False

        if dataType is int and not self.__isInteger(default):
            self.__logWrongExpectationDataType(section,key,dataType,default);
            return False

        if dataType is float and not self.___isFloat(default):
            self.__logWrongExpectationDataType(section,key,dataType,default);
            return False

        if dataType is bool and not self.__isBoolean(default):
            self.__logWrongExpectationDataType(section,key,dataType,default);
            return False

        if self.__isInteger(section) or self.___isFloat(section) or self.__isBoolean(section):
            log.warning("Section names must be strings, passed name = [{}]".format(section))
            return False

        if self.__isInteger(key) or self.___isFloat(key) or self.__isBoolean(key):
            log.warning("Section names must be strings, passed name = [{}]".format(section))
            return False

        entryExists,position = self.expectationExistsAtIndex(section,key)
        if entryExists:
            log.warning("Attempting to and entry which already exists. Section: [{}], Key [{}]".format(section,key))
            return False

        if not str(key).islower():
            log.warning("Converting key [{}] to all lower case".format(key))

        newExpection = {
            'section' : section,
            'key' :  str(key).lower(),
            'value' : None,
            'dataType' : dataType,
            'default' : default,
            'message' : message,
            }
        self.__expectations.append(newExpection)
        log.debug("Added new expectation with Section: [{}], Key [{}], DataType [{}], Default [{}]".format(section,key,dataType,default))
        return True

    def __logWrongExpectationDataType(self,section,key,dataType,default):
        log.warning("Trying to set expectation Section: [{}], Key [{}], Default [{}] with wrong data type. (Type = [{}])".format(section,key,default,dataType))

    def removeExpectation(self,section,key):
        entryExist, position = self.expectationExistsAtIndex(section,key)
        if entryExist:
            log.debug("Removing expectation with Section: [{}], Key [{}]".format(section,key))
            self.__expectations.pop(position)
            return True
        else:
            log.warning("Trying to remove expectation which doesn't exist. Section: [{}], Key [{}]".format(section,key))
            return False

    def expectationExistsAtIndex(self,section,key):
        for i,expectation in enumerate(self.__expectations):
            if expectation['section'] == section and expectation['key'] == key:
                return True,i
        return False,None

    def getValue(self,section,key):
        entryExists, position = self.expectationExistsAtIndex(section,key)
        if entryExists:
            return self.__expectations[position]['value']
        log.warning("Trying to retreive a value for an expectation which doean't exist. Section: [{}], Key [{}]".format(section,key))
        return None

    def setValue(self,section,key,value):
        if not self.__configReady:
            log.warning("Change the value of an expection with Section: [{}], Key: [{}], Value: [{}] when target file not set. Call setConfigurationFile first".format(
                section,key,value))
            return False
        entryExists, position = self.expectationExistsAtIndex(section,key)
        if entryExists:
            if self.__expectations[position]['dataType'] is int:
                if self.__isInteger(value):
                    self.__logValueUpdate(section,key,value,position,True)
                    self.__expectations[position]['value'] = value
                    return True
                else:
                    self.__logValueUpdate(section,key,value,position,False)
                    return False
            elif self.__expectations[position]['dataType'] is float:
                if self.___isFloat(value):
                    self.__logValueUpdate(section,key,value,position,True)
                    self.__expectations[position]['value'] = value
                    return True
                else:
                    self.__logValueUpdate(section,key,value,position,False)
                    return False
            elif self.__expectations[position]['dataType'] is bool:
                if self.__isBoolean(value):
                    self.__logValueUpdate(section,key,value,position,True)
                    self.__expectations[position]['value'] = value
                    return True
                else:
                    self.__logValueUpdate(section,key,value,position,False)
                    return False
            else:
                self.__expectations[position]['value'] = value
                self.__logValueUpdate(section,key,value,position,True)
                return True
        else:
            log.warning("Cannot update the value of Section [{}], Key [{}] to [{}], entry doesn't exists in expectation list".format(section,key,value))
            return False

    def __logValueUpdate(self,section,key,value,position,success):
        if success:
            log.debug("Updated the value of Section [{}], Key [{}], from [{}] to [{}]".format(section,key,self.__expectations[position]['value'],value))
        else:
            log.warning("Cannot update the value of Section [{}], Key [{}], from [{}] to [{}], wrong type (type = [{}])".format(section,
                key,self.__expectations[position]['value'],value,self.__expectations[position]['dataType']))

    def __isInteger(self,value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def ___isFloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def __isBoolean(self,value):
        return type(value) == bool

    def printExpectations(self):
        print("Configuration Values")
        for expectation in self.__expectations:
            print()
            print("Section:\t",expectation['section'])
            print("Key\t\t",expectation['key'])
            print("Data Type:\t",expectation['dataType'])
            print("Value:\t\t",expectation['value'])
            print("Default Value:\t",expectation['default'])

    def writeConfigurationFile(self,filename = None):

        if len(self.__expectations) == 0:
            return False

        if filename is None:
            filename = self.__configurationFile

        newConfig = ConfigParser();

        for expectation in self.__expectations:
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

        if len(self.__expectations) == 0:
            log.warning("Trying to open a configuration file '{}' with no __expectations set, nothins was loaded".format(filename))
            return False
        try:
            if len(self.__configObject.read(filename)) == 0:
                log.warning("Failed to open configuration file '{}'. Using default values for __expectations".format(filename))
                self.__loadDefaultsWhereNeeded()
                self.__configurationFile = filename;
                self.__configReady = True;
                return False
        except:
            log.warning("Failed to open configuration file '{}'. Using default values for __expectations".format(filename))
            self.__loadDefaultsWhereNeeded()
            self.__configurationFile = filename;
            self.__configReady = True;
            return False

        log.debug("Loading configuration file {}".format(filename));
        self.___parseConfigValues()
        self.__loadDefaultsWhereNeeded()
        self.__configReady = True;
        self.__configurationFile = filename;
        return True

    def __loadDefaultsWhereNeeded(self):
        for expectation in self.__expectations:
            if expectation['value'] is None:
                log.debug("Section [{}] with key [{}] not found in configuration file, using default value {}".format(expectation['section'],
                    expectation['key'],
                    expectation['default']))
                expectation['value'] = expectation['default']

    def ___parseConfigValues(self):
        for section in self.__configObject.sections():
            for key in self.__configObject[section]:
                entryExists,position = self.expectationExistsAtIndex(section,key)
                if(entryExists):
                    dataType = self.__expectations[position]['dataType']
                    if dataType is int:
                        self.__convertInt(section,key,position)
                    elif dataType is bool:
                        self.__convertBoolean(section,key,position)
                    elif dataType is float:
                        self.__convertFloat(section,key,position)
                    else:
                        self.__expectations[position]['value'] = self.__configObject.get(section,key)

    def __convertBoolean(self,section,key,position):
        try:
            self.__expectations[position]['value'] = self.__configObject.getboolean(section,key)
            self.__logConversionStatus(True,position)
        except:
            self.__expectations[position]['value'] = self.__expectations[position]['default']
            self.__logConversionStatus(False,position)

    def __convertFloat(self,section,key,position):
        try:
            self.__expectations[position]['value'] = self.__configObject.getfloat(section,key)
            self.__logConversionStatus(True,position)
        except:
            self.__expectations[position]['value'] = self.__expectations[position]['default']
            self.__logConversionStatus(False,position)

    def __convertInt(self,section,key,position):
        try:
            self.__expectations[position]['value'] = self.__configObject.getint(section,key)
            self.__logConversionStatus(True,position)
        except:
            self.__expectations[position]['value'] = self.__expectations[position]['default']
            self.__logConversionStatus(False,position)

    def __logConversionStatus(self,sucess,position):
        if sucess:
            log.debug("Updating Section [{}] with key [{}] to value [{}] found in configuration file".format(self.__expectations[position]['section'],
                self.__expectations[position]['key'],
                self.__expectations[position]['value']))
        else:
            log.warning("Section [{}] with key [{}] of configuration file cannot be parsed as [{}], using default value {}".format(self.__expectations[position]['section'],
                self.__expectations[position]['key'],
                self.__expectations[position]['dataType'],
                self.__expectations[position]['default']))
