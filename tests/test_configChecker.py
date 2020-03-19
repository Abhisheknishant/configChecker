import unittest
from configChecker import ConfigChecker

class ExpectionTests(unittest.TestCase):

    def setUp(self):
        self.checker = ConfigChecker()

    def test_adding_item_increases_length(self):
        self.checker.setExpectation("TestSection","TestKey","TestDefault");
        self.assertIs(len(self.checker.expectations),1,"Length of expectation list didn't increase when item was added.")

if __name__ == '__main__':
    unittest.main();

