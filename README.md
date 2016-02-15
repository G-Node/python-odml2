Python odML 2 prototype
=======================

Python odML 2 is a prototype for a future version of the odML metadata format and library.
The prototype serves as a testing ground for new ideas and concepts for storing and handling experimental metadata.

Using the library
-----------------

The first step is to clone the repository and `cd` into the directory:

```bash
git clone git@github.com:G-Node/python-odml2.git
cd python-odml2
```

You should now run the tests in order to check whether all dependencies (setuptools, PyYAML, nose) are 
installed on your system. 

```
python setup.py test
```
or for python 3
```
python3 setup.py test
```

Now you can already start `ipython` or `ipython notebook` and run some code that uses the library.
If you like to install the development version such that it automatically updates if you pull changes from the 
repository, you can run the following command:

```
sudo python setup.py develop
```
or for python 3
```
sudo python3 setup.py develop
```

Since all classes of `python-odml2` reside in the `odml2` package, the library does not interfere with 
with installations of the old `python-odml` library.

Current development state
-------------------------

The prototype is still in an early development phase and many features are currently not implemented. 
However some aspects of the library can already be tested. 
There is a simple ipython notebook [intro.ipynb](https://github.com/G-Node/python-odml2/blob/master/intro.ipynb) that shows the basic usage.

#### Implemented features

* Basic API design for accessing and populating documents and sections
* Value parsing
* Back-end API design and front-end back-end interaction
* Serialization and deserialization to Yaml
* Terminologies and property and section type definitions
* Terminology handling strategies
* Links between sections
* Iteration and filtering of documents

#### List of unimplemented features

* Serialization to/from other formats
* Probably many convenient functions

