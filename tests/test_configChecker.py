import unittest
from configchecker import ConfigChecker
import os
import logging
import sys
from io import StringIO

logging.disable(logging.CRITICAL)

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

expectedOutput ="Configuration Values\n\
\n\
Section:	 FirstSection\n\
Key		 key_integer\n\
Data Type:	 <class 'int'>\n\
Value:		 None\n\
Default Value:	 123\n\
"

class ExpectionTests(unittest.TestCase):

    def setUp(self):
        self.checker = ConfigChecker()

    def test_adding_item_increases_length(self):
        self.checker.set_expectation("TestSection","TestKey",bool,False);
        added = self.checker.set_expectation("TestSection_second","TestKey",bool,True);
        self.assertIs(len(self.checker.get_expectations()),2,"Length of expectation list didn't increase when item was added.")
        self.assertIs(added,True)

    def test_adding_duplicate_expectation_dont_duplicate(self):
        self.checker.set_expectation("TestSection","testKey",str,"TestDefault");
        added = self.checker.set_expectation("TestSection","testkey",str,"TestDefault");
        self.assertIs(len(self.checker.get_expectations()),1,"Length of expectation list didn't increase when item was added.")
        self.assertIs(added,False)

    def test_adding_duplicate_key_different_section_is_ok(self):
        self.checker.set_expectation("TestSection","testKey",int,123);
        added = self.checker.set_expectation("TestSection_test","testkey",int,1234);
        self.assertIs(len(self.checker.get_expectations()),2,"Length of expectation list didn't increase when item was added.")
        self.assertIs(added,True)

    def test_expectation_added_to_end_of_list_correctly_no_message(self):
        self.checker.set_expectation("TestSection","testkey",int,34);
        addedSection = self.checker.get_expectations()[len(self.checker.get_expectations()) - 1]['section']
        addedKey = self.checker.get_expectations()[len(self.checker.get_expectations()) - 1]['key']
        addedType = self.checker.get_expectations()[len(self.checker.get_expectations()) - 1]['data_type']
        addedDefault = self.checker.get_expectations()[len(self.checker.get_expectations()) - 1]['default']
        addedMessage = self.checker.get_expectations()[len(self.checker.get_expectations() ) - 1]['message']
        self.assertEqual(addedSection,'TestSection',"Added section doesn't match last section in list")
        self.assertEqual(addedKey,'testkey',"Added key doesn't match last key in list")
        self.assertEqual(addedType,int,"Added type doesn't match last type in list")
        self.assertEqual(addedDefault,34,"Added default doesn't match last default in list")
        self.assertEqual(addedMessage,None,"Added message doesn't match last message in list")

    def test_expectation_added_to_end_of_list_correctly_with_message(self):
        self.checker.set_expectation("TestSection","testkey",str,"TestDefault","TestMessage");
        addedSection = self.checker.get_expectations()[len(self.checker.get_expectations()) - 1]['section']
        addedKey = self.checker.get_expectations()[len(self.checker.get_expectations()) - 1]['key']
        addedType = self.checker.get_expectations()[len(self.checker.get_expectations()) - 1]['data_type']
        addedDefault = self.checker.get_expectations()[len(self.checker.get_expectations()) - 1]['default']
        addedMessage = self.checker.get_expectations()[len(self.checker.get_expectations() ) - 1]['message']
        self.assertEqual(addedSection,'TestSection',"Added section doesn't match last section in list")
        self.assertEqual(addedKey,'testkey',"Added key doesn't match last key in list")
        self.assertEqual(addedType,str,"Added type doesn't match last type in list")
        self.assertEqual(addedDefault,'TestDefault',"Added default doesn't match last default in list")
        self.assertEqual(addedMessage,'TestMessage',"Added message doesn't match last message in list")

    def test_removeing_expectation_which_matches_section_and_key_reduces_list_number(self):
        self.checker.set_expectation("TestSection","testkey_2",bool,False,"TestMessage")
        self.checker.set_expectation("TestSection","testkey",int,23498,"TestMessage")
        removed = self.checker.remove_expectation("TestSection",'testkey')
        entryExists,position = self.checker.expectation_exists_at_index("TestSection","testkey_2")
        self.assertIs(len(self.checker.get_expectations()),1,"Matching expectation wasn't removed from list.")
        self.assertIs(position,0)
        self.assertIs(entryExists,True)
        self.assertIs(removed,True)

    def test_removeing_expectation_which_doesnt_match_section_and_key_returns_false(self):
        self.checker.set_expectation("TestSection","testkey_2",bool,False,"TestMessage")
        self.checker.set_expectation("TestSection","testkey",int,23498,"TestMessage")
        removed = self.checker.remove_expectation("badSecion",'testkey')
        entryExists,position = self.checker.expectation_exists_at_index("TestSection","testkey_2")
        self.assertIs(entryExists,True)
        entryExists,position = self.checker.expectation_exists_at_index("TestSection","testkey")
        self.assertIs(entryExists,True)
        self.assertIs(len(self.checker.get_expectations()),2)
        self.assertIs(removed,False)

    def test_adding_expectation_with_wrong_default_type_returns_false_integer(self):
        added = self.checker.set_expectation("FirstSection","key_integer",int,'asdfasd',"TestMessage")
        self.assertIs(added,False);
        self.assertIs(len(self.checker.get_expectations()),0)

    def test_adding_expectation_with_wrong_default_type_returns_false_float(self):
        added = self.checker.set_expectation("FirstSection","key_float",float,'asdfasd',"TestMessage")
        self.assertIs(added,False);
        self.assertIs(len(self.checker.get_expectations()),0)

    def test_adding_expectation_with_wrong_default_type_returns_false_boolean(self):
        added = self.checker.set_expectation("FirstSection","key_float",bool,'asdfasd',"TestMessage")
        self.assertIs(added,False);
        self.assertIs(len(self.checker.get_expectations()),0)

    def test_adding_expectation_with_not_allowed_data_type_returns_false(self):
        added = self.checker.set_expectation("FirstSection","key_float",'asdf','asdfasd',"TestMessage")
        self.assertIs(added,False);
        self.assertIs(len(self.checker.get_expectations()),0)

    def test_section_names_cant_be_integer(self):
        added = self.checker.set_expectation(123,"key_float",float,123.3,"TestMessage")
        self.assertIs(added,False);

    def test_section_names_cant_be_floats(self):
        added = self.checker.set_expectation(1232.12,"key_float",float,123.3,"TestMessage")
        self.assertIs(added,False);

    def test_section_names_cant_be_boolean(self):
        added = self.checker.set_expectation(True,"key_float",float,123.3,"TestMessage")
        self.assertIs(added,False);

    def test_key_names_cant_be_integer(self):
        added = self.checker.set_expectation('Section',123,float,123.3,"TestMessage")
        self.assertIs(added,False);

    def test_key_names_cant_be_floats(self):
        added = self.checker.set_expectation('Section',123.123,float,123.3,"TestMessage")
        self.assertIs(added,False);

    def test_key_names_cant_be_boolean(self):
        added = self.checker.set_expectation('Section',True,float,123.3,"TestMessage")
        self.assertIs(added,False);

    def test_printing_expectation_output(self):
        added = self.checker.set_expectation("FirstSection","key_integer",int,123)
        old_stdout = sys.stdout
        sys.stdout = printOutput = StringIO()
        self.checker.print_expectations()
        sys.stdout = old_stdout
        self.assertEqual(printOutput.getvalue(),expectedOutput)

class FileOperationTests(unittest.TestCase):

    def setUp(self):
        self.checker = ConfigChecker()
        self.makeGoodConfigFile()
        self.makeBadConfigFile()

    def tearDown(self):
        self.removeGoodConfigFile()
        self.removeBadConfigFile()
        try:
            os.remove('test_write.ini')
        except:
            pass

    def test_opening_bad_config_file_return_false(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.set_configuration_file('test_bad_config.ini')
        self.assertIs(opened,False)

    def test_opening_file_with_no_dxpectations_returns_false(self):
        opened = self.checker.set_configuration_file('test_good_config.ini')
        self.assertIs(opened,False)

    def test_file_which_exists_opens_correctly(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.set_configuration_file('test_good_config.ini')
        self.assertIs(len(self.checker.get_config_parser_object().sections()),3, "A well fomatted config file contained no sections when opened")
        self.assertIs(opened,True,"Opened was reported for a well formatted config file")

    def test_file_which_doesnt_exist_returns_false(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.set_configuration_file('bad_file_name.ini')
        self.assertIs(len(self.checker.get_config_parser_object().sections()),0, "A file which didn't exist resulted in config sections being made.")
        self.assertIs(opened,False,"A file which didn't exist resulted in a true open status (should be false)")

    def test_only_expectation_are_stored_as_config_values_after_file_is_read(self):
        opened = self.checker.set_configuration_file('test_good_config.ini')
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.set_expectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.assertIs(len(self.checker.get_expectations()),2)

    def test_expectations_which_match_have_their_value_updated(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.set_expectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.checker.set_expectation("FirstSection","key_float",float,12123.1,"TestMessage")
        self.checker.set_expectation("FirstSection","key_string",str,'A string',"TestMessage")
        opened = self.checker.set_configuration_file('test_good_config.ini')
        self.assertIs(self.checker.get_value("FirstSection","key_integer"),45)
        self.assertIs(self.checker.get_value("FirstSection","key_boolean"),True)
        self.assertEqual(self.checker.get_value("FirstSection","key_float"),23.2)
        self.assertEqual(self.checker.get_value("FirstSection","key_string"),"I am a string")

    def test_bad_data_types_cause_their_default_to_be_loaded_bool(self):
        self.checker.set_expectation("FirstSection","key_integer",bool,True,"TestMessage")
        opened = self.checker.set_configuration_file('test_good_config.ini')
        self.assertIs(self.checker.get_value("FirstSection","key_integer"),True)

    def test_bad_data_types_cause_their_default_to_be_loaded_float(self):
        self.checker.set_expectation("FirstSection","key_string",float,123.1,"TestMessage")
        opened = self.checker.set_configuration_file('test_good_config.ini')
        self.assertIs(self.checker.get_value("FirstSection","key_string"),123.1)

    def test_bad_data_types_cause_their_default_to_be_loaded_int(self):
        self.checker.set_expectation("FirstSection","key_string",int,10,"TestMessage")
        opened = self.checker.set_configuration_file('test_good_config.ini')
        self.assertIs(self.checker.get_value("FirstSection","key_string"),10)

    def test_reading_value_not_updated_by_config_file_returns_default(self):
        self.checker.set_expectation("FirstSection","unspec_key",int,23,"TestMessage")
        opened = self.checker.set_configuration_file('test_good_config.ini')
        self.assertIs(self.checker.get_value("FirstSection","unspec_key"),23)

    def test_values_are_set_to_default_if_file_cant_be_opened(self):
        self.checker.set_expectation("FirstSection","unspec_key",int,23,"TestMessage")
        opened = self.checker.set_configuration_file('random_file_name.ini')
        self.assertIs(self.checker.get_value("FirstSection","unspec_key"),23)

    def test_writing_file_produces_produces_expected_result(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.set_expectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.checker.set_expectation("FirstSection","key_float",float,12123.1,"TestMessage")
        self.checker.set_expectation("FirstSection","key_string",str,'A string',"TestMessage")
        self.checker.set_expectation("SecondSection","key_string",str,'default',"TestMessage")

        opened = self.checker.set_configuration_file('test_write.ini')
        self.assertIs(opened,False)
        written = self.checker.write_configuration_file('test_write.ini')
        self.assertIs(written,True)

        # Make a new object and set get_expectations() to different values
        self.checker = ConfigChecker()
        self.checker.set_expectation("FirstSection","key_integer",int,1,"TestMessage")
        self.checker.set_expectation("FirstSection","key_boolean",bool,True,"TestMessage")
        self.checker.set_expectation("FirstSection","key_float",float,1.1,"TestMessage")
        self.checker.set_expectation("FirstSection","key_string",str,'sfs',"TestMessage")
        self.checker.set_expectation("SecondSection","key_string",str,'asfs',"TestMessage")

        # If the values match the original dump then all everythin was successful
        opened = self.checker.set_configuration_file('test_write.ini')

        self.assertIs(opened,True)
        self.assertIs(self.checker.get_value("FirstSection","key_integer"),23)
        self.assertIs(self.checker.get_value("FirstSection","key_boolean"),False)
        self.assertEqual(self.checker.get_value("FirstSection","key_float"),12123.1)
        self.assertEqual(self.checker.get_value("FirstSection","key_string"),"A string")
        self.assertEqual(self.checker.get_value("SecondSection","key_string"),"default")

        os.remove('test_write.ini')

    def test_writing_file_with_none_uses_existing_config_file_name(self):

        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.set_expectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.checker.set_expectation("FirstSection","key_float",float,12123.1,"TestMessage")
        self.checker.set_expectation("FirstSection","key_string",str,'A string',"TestMessage")
        self.checker.set_expectation("SecondSection","key_string",str,'default',"TestMessage")

        opened = self.checker.set_configuration_file('test_write.ini')
        self.assertIs(opened,False)
        written = self.checker.write_configuration_file(None)
        self.assertIs(written,True)
        self.assertIs(os.path.exists('test_write.ini'),True)

        os.remove('test_write.ini')

    def test_writing_file_permission_error_returs_false(self):

        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.set_expectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.checker.set_expectation("FirstSection","key_float",float,12123.1,"TestMessage")
        self.checker.set_expectation("FirstSection","key_string",str,'A string',"TestMessage")
        self.checker.set_expectation("SecondSection","key_string",str,'default',"TestMessage")

        opened = self.checker.set_configuration_file('test_write.ini')
        self.assertIs(opened,False)
        written = self.checker.write_configuration_file('/root/test_config.ini')
        self.assertIs(written,False,"These tests and module shouldn't be run with root acccess.")

    def test_writing_os_error_returs_false(self):

        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.set_expectation("FirstSection","key_boolean",bool,False,"TestMessage")
        self.checker.set_expectation("FirstSection","key_float",float,12123.1,"TestMessage")
        self.checker.set_expectation("FirstSection","key_string",str,'A string',"TestMessage")
        self.checker.set_expectation("SecondSection","key_string",str,'default',"TestMessage")

        opened = self.checker.set_configuration_file('test_write.ini')
        self.assertIs(opened,False)
        written = self.checker.write_configuration_file('sdf/asdf')
        self.assertIs(written,False)

    def test_writing_file_with_no_expectations_returns_false(self):
        written = self.checker.write_configuration_file('test_write.ini')
        self.assertIs(written,False)

    def test_can_change_the_value_of_an_expectation_int(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.set_configuration_file('test_write.ini')
        written = self.checker.set_value("FirstSection","key_integer",45);
        self.assertIs(written,True)
        self.assertIs(self.checker.get_value("FirstSection","key_integer"),45)

    def test_can_change_the_value_of_an_expectation_float(self):
        self.checker.set_expectation("FirstSection","key_float",float,23.3,"TestMessage")
        opened = self.checker.set_configuration_file('test_write.ini')
        written = self.checker.set_value("FirstSection","key_float",45.3);
        self.assertIs(written,True)
        self.assertIs(self.checker.get_value("FirstSection","key_float"),45.3)

    def test_can_change_the_value_of_an_expectation_bool(self):
        self.checker.set_expectation("FirstSection","key_boolean",bool,True,"TestMessage")
        opened = self.checker.set_configuration_file('test_write.ini')
        written = self.checker.set_value("FirstSection","key_boolean",False);
        self.assertIs(written,True)
        self.assertIs(self.checker.get_value("FirstSection","key_boolean"),False)

    def test_can_change_the_value_of_an_expectation_str(self):
        self.checker.set_expectation("FirstSection","key_string",str,'asdf',"TestMessage")
        opened = self.checker.set_configuration_file('test_write.ini')
        written = self.checker.set_value("FirstSection","key_string",'qwer');
        self.assertIs(written,True)
        self.assertIs(self.checker.get_value("FirstSection","key_string"),'qwer')

    def test_can_change_the_value_of_multiple_without_changing_others(self):
        self.checker.set_expectation("FirstSection","key_string",str,'asdf',"TestMessage")
        self.checker.set_expectation("FirstSection","key_boolean",bool,True,"TestMessage")
        self.checker.set_expectation("FirstSection","key_float",float,23.3,"TestMessage")
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")

        opened = self.checker.set_configuration_file('test_write.ini')

        written = self.checker.set_value("FirstSection","key_string",'qwer');
        self.assertIs(written,True)
        written = self.checker.set_value("FirstSection","key_float",45.3);
        self.assertIs(written,True)
        written = self.checker.set_value("FirstSection","key_integer",45);
        self.assertIs(written,True)
        written = self.checker.set_value("FirstSection","key_boolean",False);
        self.assertIs(written,True)

        self.assertIs(self.checker.get_value("FirstSection","key_string"),'qwer')
        self.assertIs(self.checker.get_value("FirstSection","key_integer"),45)
        written = self.checker.set_value("FirstSection","key_float",45.3);
        self.assertIs(self.checker.get_value("FirstSection","key_boolean"),False)

    def test_changing_value_of_expectation_which_doesnt_exist_returns_false(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.set_configuration_file('test_write.ini')
        written = self.checker.set_value("WrongSection","key_integer",45);
        self.assertIs(written,False)

    def test_cannot_set_values_if_file_target_is_not_set(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        written = self.checker.set_value("FirstSection","key_integer",45);
        self.assertIs(written,False)

    def test_writing_incorrect_type_returns_false_integer(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        opened = self.checker.set_configuration_file('test_write.ini')
        written = self.checker.set_value("FirstSection","key_integer",'sdfs');
        self.assertIs(written,False)

    def test_writing_incorrect_type_returns_false_float(self):
        self.checker.set_expectation("FirstSection","key_float",float,23.3,"TestMessage")
        opened = self.checker.set_configuration_file('test_write.ini')
        written = self.checker.set_value("FirstSection","key_float",'sdfs');
        self.assertIs(written,False)

    def test_writing_incorrect_type_returns_false_bool(self):
        self.checker.set_expectation("FirstSection","key_boolean",bool,False,"TestMessage")
        opened = self.checker.set_configuration_file('test_write.ini')
        written = self.checker.set_value("FirstSection","key_boolean",'sdf');
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
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.get_expectations()[0]['value'] = 12;
        self.assertIs(self.checker.get_value("FirstSection","key_integer"),12)

    def test_reading_bad_section_or_bad_key_returns_None(self):
        self.checker.set_expectation("FirstSection","key_integer",int,23,"TestMessage")
        self.checker.get_expectations()[0]['value'] = 12;
        self.assertIs(self.checker.get_value("BadSection","key_integer"),None)
        self.assertIs(self.checker.get_value("FirstSection","badKey"),None)

if __name__ == '__main__':
    unittest.main();
