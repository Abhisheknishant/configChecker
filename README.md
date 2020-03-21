[![Build Status](https://travis-ci.org/stuianna/configChecker.svg?branch=master)](https://travis-ci.org/stuianna/configChecker)
[![Codecov](https://img.shields.io/codecov/c/github/stuianna/configChecker)](https://codecov.io/gh/stuianna/configChecker)
![GitHub](https://img.shields.io/github/license/stuianna/configChecker)

# Python Config Checker

Python module wrapper around `ConfigParser` to ensure strict operation when working with configuration (.ini) files.

## Example Usage

Assume a configuration file, `config.ini`, with the following content:

```
[General]
api_key = api-private-key
conversion_factor = 123.456
print_results = False
```

Config parser can be used to ensure the expected values appear in the file, with default values used as substitutes.

```python
from comfigparser import ConfigParser

config = ConfigChecker()

# Set the configuration values which are to be used.
# setExpectation(SectionName,SectionOption,DataType,DefaultValue)
config.setExpectation('General','api_key',str,'api-private-key')
config.setExpectation('General','retries',int,5)
config.setExpectation('General','conversion_factor',float,3.14)
config.setExpectation('General','print_results',bool,True)

# Try to load a configuration (.ini) file.
# Any previously set expectation which exists in the file has its value updated.
# Any value which doesn't exist in the file using the default value.
# Any configuration value in the file which isn't an expectation is ignored.
# This should be called before a file is written, or configuration value set or get
config.setConfigurationFile('config.ini')

# Get the value of a configuration variable
printResults = config.getValue("General','print_results')

# Set the value of a configuration variable
config.setValue('General','api_key','123-23423csdfs3-2342-234')

# Write a configuration (.ini) file.
# This operation creates a new file with all the previously set expectations
# If a value hasn't been added for the option, then the default value is used.
config.writeConfigurationFile('config.ini')
```

The resulting (new) configuration file look as follows:
```ini
[General]
api_key = 123-23423csdfs3-2342-234
retries = 5
conversion_factor = 123.456
print_results = False
```
Notice the option `retries` has been added with the default value based on the expectation, and the `api_key` has been updated. The values of `conversion_factor` and `print_results` remained unchanged, as they existed in the original configuration file.


## Development

```sh
git clone https://github.com/stuianna/configChecker.git
cd configChecker
virtualenv configChecker
source configChecker/bin/activate
pip install -r requirements.txt
```
