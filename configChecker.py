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

    def get_expectations(self):
        return self.__expectations

    def get_config_parser_object(self):
        return self.__configObject

    def set_expectation(self,section,key,dataType,default,message = None):

        if dataType not in [bool,float,str,int]:
            log.warning("Trying to add expection with not allowed data type [{}]. Allowed types = [bool, int, str, float]".format(dataType))
            return False

        if dataType is int and not self.__is_integer(default):
            self.__log_wrong_expectation_data_type(section,key,dataType,default);
            return False

        if dataType is float and not self.___is_float(default):
            self.__log_wrong_expectation_data_type(section,key,dataType,default);
            return False

        if dataType is bool and not self.__is_boolean(default):
            self.__log_wrong_expectation_data_type(section,key,dataType,default);
            return False

        if self.__is_integer(section) or self.___is_float(section) or self.__is_boolean(section):
            log.warning("Section names must be strings, passed name = [{}]".format(section))
            return False

        if self.__is_integer(key) or self.___is_float(key) or self.__is_boolean(key):
            log.warning("Section names must be strings, passed name = [{}]".format(section))
            return False

        entryExists,position = self.expectation_exists_at_index(section,key)
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

    def __log_wrong_expectation_data_type(self,section,key,dataType,default):
        log.warning("Trying to set expectation Section: [{}], Key [{}], Default [{}] with wrong data type. (Type = [{}])".format(section,key,default,dataType))

    def remove_expectation(self,section,key):
        entryExist, position = self.expectation_exists_at_index(section,key)
        if entryExist:
            log.debug("Removing expectation with Section: [{}], Key [{}]".format(section,key))
            self.__expectations.pop(position)
            return True
        else:
            log.warning("Trying to remove expectation which doesn't exist. Section: [{}], Key [{}]".format(section,key))
            return False

    def expectation_exists_at_index(self,section,key):
        for i,expectation in enumerate(self.__expectations):
            if expectation['section'] == section and expectation['key'] == key:
                return True,i
        return False,None

    def get_value(self,section,key):
        entryExists, position = self.expectation_exists_at_index(section,key)
        if entryExists:
            return self.__expectations[position]['value']
        log.warning("Trying to retreive a value for an expectation which doean't exist. Section: [{}], Key [{}]".format(section,key))
        return None

    def set_value(self,section,key,value):
        if not self.__configReady:
            log.warning("Change the value of an expection with Section: [{}], Key: [{}], Value: [{}] when target file not set. Call set_configuration_file first".format(
                section,key,value))
            return False
        entryExists, position = self.expectation_exists_at_index(section,key)
        if entryExists:
            if self.__expectations[position]['dataType'] is int:
                if self.__is_integer(value):
                    self.__log_value_update(section,key,value,position,True)
                    self.__expectations[position]['value'] = value
                    return True
                else:
                    self.__log_value_update(section,key,value,position,False)
                    return False
            elif self.__expectations[position]['dataType'] is float:
                if self.___is_float(value):
                    self.__log_value_update(section,key,value,position,True)
                    self.__expectations[position]['value'] = value
                    return True
                else:
                    self.__log_value_update(section,key,value,position,False)
                    return False
            elif self.__expectations[position]['dataType'] is bool:
                if self.__is_boolean(value):
                    self.__log_value_update(section,key,value,position,True)
                    self.__expectations[position]['value'] = value
                    return True
                else:
                    self.__log_value_update(section,key,value,position,False)
                    return False
            else:
                self.__expectations[position]['value'] = value
                self.__log_value_update(section,key,value,position,True)
                return True
        else:
            log.warning("Cannot update the value of Section [{}], Key [{}] to [{}], entry doesn't exists in expectation list".format(section,key,value))
            return False

    def __log_value_update(self,section,key,value,position,success):
        if success:
            log.debug("Updated the value of Section [{}], Key [{}], from [{}] to [{}]".format(section,key,self.__expectations[position]['value'],value))
        else:
            log.warning("Cannot update the value of Section [{}], Key [{}], from [{}] to [{}], wrong type (type = [{}])".format(section,
                key,self.__expectations[position]['value'],value,self.__expectations[position]['dataType']))

    def __is_integer(self,value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def ___is_float(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def __is_boolean(self,value):
        return type(value) == bool

    def print_expectations(self):
        print("Configuration Values")
        for expectation in self.__expectations:
            print()
            print("Section:\t",expectation['section'])
            print("Key\t\t",expectation['key'])
            print("Data Type:\t",expectation['dataType'])
            print("Value:\t\t",expectation['value'])
            print("Default Value:\t",expectation['default'])

    def write_configuration_file(self,filename = None):

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

    def set_configuration_file(self,filename):

        if len(self.__expectations) == 0:
            log.warning("Trying to open a configuration file '{}' with no __expectations set, nothins was loaded".format(filename))
            return False
        try:
            if len(self.__configObject.read(filename)) == 0:
                log.warning("Failed to open configuration file '{}'. Using default values for __expectations".format(filename))
                self.__load_defaults_where_needed()
                self.__configurationFile = filename;
                self.__configReady = True;
                return False
        except:
            log.warning("Failed to open configuration file '{}'. Using default values for __expectations".format(filename))
            self.__load_defaults_where_needed()
            self.__configurationFile = filename;
            self.__configReady = True;
            return False

        log.debug("Loading configuration file {}".format(filename));
        self.___parse_config_values()
        self.__load_defaults_where_needed()
        self.__configReady = True;
        self.__configurationFile = filename;
        return True

    def __load_defaults_where_needed(self):
        for expectation in self.__expectations:
            if expectation['value'] is None:
                log.debug("Section [{}] with key [{}] not found in configuration file, using default value {}".format(expectation['section'],
                    expectation['key'],
                    expectation['default']))
                expectation['value'] = expectation['default']

    def ___parse_config_values(self):
        for section in self.__configObject.sections():
            for key in self.__configObject[section]:
                entryExists,position = self.expectation_exists_at_index(section,key)
                if(entryExists):
                    dataType = self.__expectations[position]['dataType']
                    if dataType is int:
                        self.__convert_int(section,key,position)
                    elif dataType is bool:
                        self.__convert_boolean(section,key,position)
                    elif dataType is float:
                        self.__convert_float(section,key,position)
                    else:
                        self.__expectations[position]['value'] = self.__configObject.get(section,key)

    def __convert_boolean(self,section,key,position):
        try:
            self.__expectations[position]['value'] = self.__configObject.getboolean(section,key)
            self.__log_conversion_status(True,position)
        except:
            self.__expectations[position]['value'] = self.__expectations[position]['default']
            self.__log_conversion_status(False,position)

    def __convert_float(self,section,key,position):
        try:
            self.__expectations[position]['value'] = self.__configObject.getfloat(section,key)
            self.__log_conversion_status(True,position)
        except:
            self.__expectations[position]['value'] = self.__expectations[position]['default']
            self.__log_conversion_status(False,position)

    def __convert_int(self,section,key,position):
        try:
            self.__expectations[position]['value'] = self.__configObject.getint(section,key)
            self.__log_conversion_status(True,position)
        except:
            self.__expectations[position]['value'] = self.__expectations[position]['default']
            self.__log_conversion_status(False,position)

    def __log_conversion_status(self,sucess,position):
        if sucess:
            log.debug("Updating Section [{}] with key [{}] to value [{}] found in configuration file".format(self.__expectations[position]['section'],
                self.__expectations[position]['key'],
                self.__expectations[position]['value']))
        else:
            log.warning("Section [{}] with key [{}] of configuration file cannot be parsed as [{}], using default value {}".format(self.__expectations[position]['section'],
                self.__expectations[position]['key'],
                self.__expectations[position]['dataType'],
                self.__expectations[position]['default']))
