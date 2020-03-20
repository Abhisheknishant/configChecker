import unittest
from configChecker import ConfigChecker
import os

good_config = \
"[FirstSection]\n\
key_integer = 45 \n\
key_boolean = yes \n\
key_float = 23.2\n\
key_string = I am a string\n\
\n\
[SecondSection] \n\
User = hg \n\
\n\
[ThirdSection]\n\
Port = 50022 \n\
ForwardX11 = no\n"

bad_config = "[asdff} asdfas[sd"

class ExpectionTests(unittest.TestCase):

    def setUp(self):
        self.checker = ConfigChecker()

    def test_adding_item_increases_length(self):
        self.checker.setExpectation("TestSection","TestKey",'TestType',"TestDefault");
        self.checker.setExpectation("TestSection_second","TestKey",'TestType',"TestDefault");
        self.assertIs(len(self.checker.expectations),2,"Length of expectation list didn't increase when item was added.")

    def test_adding_duplicate_expectation_dont_duplicate(self):
        self.checker.setExpectation("TestSection","TestKey",'TestType',"TestDefault");
        self.checker.setExpectation("TestSection","TestKey",'TestType',"TestDefault");
        self.assertIs(len(self.checker.expectations),1,"Length of expectation list didn't increase when item was added.")

    def test_adding_duplicate_key_different_section_is_ok(self):
        self.checker.setExpectation("TestSection","TestKey",'TestType',"TestDefault");
        self.checker.setExpectation("TestSection_test","TestKey",'TestType',"TestDefault");
        self.assertIs(len(self.checker.expectations),2,"Length of expectation list didn't increase when item was added.")

    def test_expectation_added_to_end_of_list_correctly_no_message(self):
        self.checker.setExpectation("TestSection","TestKey","TestType","TestDefault");
        addedSection = self.checker.expectations[len(self.checker.expectations) - 1]['section']
        addedKey = self.checker.expectations[len(self.checker.expectations) - 1]['key']
        addedType = self.checker.expectations[len(self.checker.expectations) - 1]['dataType']
        addedDefault = self.checker.expectations[len(self.checker.expectations) - 1]['default']
        addedMessage = self.checker.expectations[len(self.checker.expectations ) - 1]['message']
        self.assertEqual(addedSection,'TestSection',"Added section doesn't match last section in list")
        self.assertEqual(addedKey,'TestKey',"Added key doesn't match last key in list")
        self.assertEqual(addedType,'TestType',"Added type doesn't match last type in list")
        self.assertEqual(addedDefault,'TestDefault',"Added default doesn't match last default in list")
        self.assertEqual(addedMessage,None,"Added message doesn't match last message in list")

    def test_expectation_added_to_end_of_list_correctly_with_message(self):
        self.checker.setExpectation("TestSection","TestKey",str,"TestDefault","TestMessage");
        addedSection = self.checker.expectations[len(self.checker.expectations) - 1]['section']
        addedKey = self.checker.expectations[len(self.checker.expectations) - 1]['key']
        addedType = self.checker.expectations[len(self.checker.expectations) - 1]['dataType']
        addedDefault = self.checker.expectations[len(self.checker.expectations) - 1]['default']
        addedMessage = self.checker.expectations[len(self.checker.expectations ) - 1]['message']
        self.assertEqual(addedSection,'TestSection',"Added section doesn't match last section in list")
        self.assertEqual(addedKey,'TestKey',"Added key doesn't match last key in list")
        self.assertEqual(addedType,str,"Added type doesn't match last type in list")
        self.assertEqual(addedDefault,'TestDefault',"Added default doesn't match last default in list")
        self.assertEqual(addedMessage,'TestMessage',"Added message doesn't match last message in list")

    def test_removeing_expectation_which_matches_section_and_key_reduces_list_number(self):
        self.checker.setExpectation("TestSection","TestKey_2",'TestType',"TestDefault","TestMessage")
        self.checker.setExpectation("TestSection","TestKey",'TestType',"TestDefault","TestMessage")
        self.checker.removeExpectation("TestSection",'TestKey')
        entryExists,position = self.checker.expectationExistsAtIndex("TestSection","TestKey_2")
        self.assertIs(len(self.checker.expectations),1,"Matching expectation wasn't removed from list.")
        self.assertIs(position,0)
        self.assertIs(entryExists,True)

class FileOperationTests(unittest.TestCase):

    def setUp(self):
        self.checker = ConfigChecker()
        self.makeGoodConfigFile()
        self.makeBadConfigFile()

    def tearDown(self):
        self.removeGoodConfigFile()
        self.removeBadConfigFile()

    def test_opening_bad_config_file_return_false(self):
        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.setConfigurationFile('test_bad_config.ini')
        self.assertIs(opened,False)

    def test_opening_file_with_no_expectations_returns_false(self):
        opened = self.checker.setConfigurationFile('test_good_config.ini')
        self.assertIs(opened,False)

    def test_file_which_exists_opens_correctly(self):
        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.setConfigurationFile('test_good_config.ini')
        self.assertIs(len(self.checker.configObject.sections()),3, "A well fomatted config file contained no sections when opened")
        self.assertIs(opened,True,"Opened was reported for a well formatted config file")

    def test_file_which_doesnt_exist_returns_false(self):
        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.setConfigurationFile('bad_file_name.ini')
        self.assertIs(len(self.checker.configObject.sections()),0, "A file which didn't exist resulted in config sections being made.")
        self.assertIs(opened,False,"A file which didn't exist resulted in a true open status (should be false)")

    def test_only_expectation_are_stored_as_config_values_after_file_is_read(self):
        opened = self.checker.setConfigurationFile('test_good_config.ini')
        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.setExpectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.assertIs(len(self.checker.expectations),2)

    def test_expectations_which_match_have_their_value_updated(self):
        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.setExpectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.checker.setExpectation("FirstSection","key_float",float,12123.1,"TestMessage")
        self.checker.setExpectation("FirstSection","key_string",str,'A string',"TestMessage")
        opened = self.checker.setConfigurationFile('test_good_config.ini')
        self.assertIs(self.checker.getValue("FirstSection","key_integer"),45)
        self.assertIs(self.checker.getValue("FirstSection","key_boolean"),True)
        self.assertEqual(self.checker.getValue("FirstSection","key_float"),23.2)
        self.assertEqual(self.checker.getValue("FirstSection","key_string"),"I am a string")

    def test_bad_data_types_cause_their_default_to_be_loaded_bool(self):
        self.checker.setExpectation("FirstSection","key_integer",bool,True,"TestMessage")
        opened = self.checker.setConfigurationFile('test_good_config.ini')
        self.assertIs(self.checker.getValue("FirstSection","key_integer"),True)

    def test_bad_data_types_cause_their_default_to_be_loaded_float(self):
        self.checker.setExpectation("FirstSection","key_string",float,123.1,"TestMessage")
        opened = self.checker.setConfigurationFile('test_good_config.ini')
        self.assertIs(self.checker.getValue("FirstSection","key_string"),123.1)

    def test_bad_data_types_cause_their_default_to_be_loaded_int(self):
        self.checker.setExpectation("FirstSection","key_string",int,10,"TestMessage")
        opened = self.checker.setConfigurationFile('test_good_config.ini')
        self.assertIs(self.checker.getValue("FirstSection","key_string"),10)

    def test_reading_value_not_updated_by_config_file_returns_default(self):
        self.checker.setExpectation("FirstSection","unspec_key",int,23,"TestMessage")
        opened = self.checker.setConfigurationFile('test_good_config.ini')
        self.assertIs(self.checker.getValue("FirstSection","unspec_key"),23)

    def test_values_are_set_to_default_if_file_cant_be_opened(self):
        self.checker.setExpectation("FirstSection","unspec_key",int,23,"TestMessage")
        opened = self.checker.setConfigurationFile('random_file_name.ini')
        self.assertIs(self.checker.getValue("FirstSection","unspec_key"),23)

    def test_writing_file_produces_produces_expected_result(self):
        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.setExpectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.checker.setExpectation("FirstSection","key_float",float,12123.1,"TestMessage")
        self.checker.setExpectation("FirstSection","key_string",str,'A string',"TestMessage")
        self.checker.setExpectation("SecondSection","key_string",str,'default',"TestMessage")

        opened = self.checker.setConfigurationFile('test_write.ini')
        self.assertIs(opened,False)
        written = self.checker.writeConfiguration('test_write.ini')
        self.assertIs(written,True)

        # Make a new object and set expectations to different values
        self.checker = ConfigChecker()
        self.checker.setExpectation("FirstSection","key_integer",int,1,"TestMessage")
        self.checker.setExpectation("FirstSection","key_boolean",bool,True,"TestMessage")
        self.checker.setExpectation("FirstSection","key_float",float,1.1,"TestMessage")
        self.checker.setExpectation("FirstSection","key_string",str,'sfs',"TestMessage")
        self.checker.setExpectation("SecondSection","key_string",str,'asfs',"TestMessage")

        # If the values match the original dump then all everythin was successful
        opened = self.checker.setConfigurationFile('test_write.ini')

        self.assertIs(opened,True)
        self.assertIs(self.checker.getValue("FirstSection","key_integer"),23)
        self.assertIs(self.checker.getValue("FirstSection","key_boolean"),False)
        self.assertEqual(self.checker.getValue("FirstSection","key_float"),12123.1)
        self.assertEqual(self.checker.getValue("FirstSection","key_string"),"A string")
        self.assertEqual(self.checker.getValue("SecondSection","key_string"),"default")

        os.remove('test_write.ini')

    def test_writing_file_permission_error_returs_false(self):

        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.setExpectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.checker.setExpectation("FirstSection","key_float",float,12123.1,"TestMessage")
        self.checker.setExpectation("FirstSection","key_string",str,'A string',"TestMessage")
        self.checker.setExpectation("SecondSection","key_string",str,'default',"TestMessage")

        opened = self.checker.setConfigurationFile('test_write.ini')
        self.assertIs(opened,False)
        written = self.checker.writeConfiguration('/root/test_config.ini')
        self.assertIs(written,False,"These tests and module shouldn't be run with root acccess.")

    def test_writing_file_with_no_expectations_returns_false(self):
        written = self.checker.writeConfiguration('test_write.ini')
        self.assertIs(written,False)

    def makeGoodConfigFile(self):
        try:
            with open('test_good_config.ini','w') as f:
                f.write(good_config)
        except:
            print("Warning: Cannot write test configuration files to filesystem, tests failed")

    def makeBadConfigFile(self):
        try:
            with open('test_bad_config.ini','w') as f:
                f.write(bad_config)
        except:
            print("Warning: Cannot write test configuration files to filesystem, tests failed")

    def removeGoodConfigFile(self):
        try:
            os.remove('test_good_config.ini')
        except:
            pass

    def removeBadConfigFile(self):
        try:
            os.remove('test_bad_config.ini')
        except:
            pass


class ReadingValuesTests(unittest.TestCase):

    def setUp(self):
        self.checker = ConfigChecker()

    def test_reading_good_section_and_key_returns_expected_results(self):
        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.expectations[0]['value'] = 12;
        self.assertIs(self.checker.getValue("FirstSection","key_integer"),12)

    def test_reading_bad_section_or_bad_key_returns_None(self):
        self.checker.setExpectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.expectations[0]['value'] = 12;
        self.assertIs(self.checker.getValue("BadSection","key_integer"),None)
        self.assertIs(self.checker.getValue("FirstSection","badKey"),None)

if __name__ == '__main__':
    unittest.main();

