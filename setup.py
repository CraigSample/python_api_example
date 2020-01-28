from os import path
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pythonapiexample',
    version='1.0.0',
    python_requires='>3.6',
    packages=find_packages(include=['pythonapiexample', 'pythonapiexample.*']),
    install_requires=[
        'pytest',
        'requests',
        'loremipsum',
        'jsonpath'
    ],
    url='https://github.com/CraigSample/python_api_example',
    license='',
    author='Craig D\'Orsay',
    author_email='craig_dorsay@yahoo.com',
    description='Test an API using Python and pytest',
    setup_requires=['flake8'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={'': ['bugs_found.txt']}
)
