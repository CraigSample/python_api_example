python_api_example: Craig D'Orsay
=====================================

What is python_api_example?
-------------------------------

python_api_example contains Python code designed to meet the
reqirements for an administered Python test:

Create a functional test suite for a simple REST API. The API stores quotes, and allows for retrieval, lookup, addition, and removal.

The test suite is to be created with Python 3.6 or newer, pytest, and requests.

The solution is to be contained entirely in a single python file (test_quotes_api.py).

A `bugs_found.txt` file has been included containing a terse description of bugs found to date from test output.


## Prerequisites

### Libraries
1. Python 3.6 or newer
2. Pytest (https://docs.pytest.org/)
3. Requests (http://docs.python-requests.org/)
4. Loremipsum (https://loremipsum.readthedocs.io/en/latest/)

## Installation
To install the code and libraries, issue a pip install.

Example:
```
$ pip3 install -e .
```

### A Running Quotes API
In order to have a successful execution, run the "quotes_server.py" file (note: this code is supplied elsewhere) using Python at a command prompt. Wait for the stdout to mention the server starting with the default host and port (127.0.0.1:6543).

Example: 
```
$ python3 quotes_server.py 
INFO:__main__:Starting server on 127.0.0.1:6543
```

## Execute the test cases
From the command prompt, run the `test_quotes_api.py` file using pytest.

Example:
```
$ py.test -s test_quotes_api.py
```
