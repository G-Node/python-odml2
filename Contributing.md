How to contribute to odML
=========================

This document gives some information about how to contribute to the python-odml2 project.

Contributing
------------

If you want to contribute to the project please first create a fork of the repository on GitHub.
When you are done with implementing a new feature or with fixing a bug, please send 
us a pull request.

If you contribute to the project regularly, it would be very much appreciated if you 
would stick to the following development workflow:

1. Select an *issue* from the issue tracker that you want to work on and assign the issue to your account. 
   If the *issue* is about a relatively complex matter or requires larger API changes the description of the 
   *issue* or its respective discussion should contain a brief concept about how the solution will look like.

2. During the implementation of the feature or bug-fix add your changes in small atomic commits.
   Commit messages should be short but expressive. 
   The first line of the message should not exceed **50** characters and the 2nd line should be empty. 
   If you want to add further text you can do so from the 3rd line on without limitations.
   If possible reference fixed issues in the commit message (e.g. "fixes #101"). 

3. When done with the implementation, run the unit tests with python 2.7 and python 3.4.
   
4. Send us a pull request with your changes. 
   The pull request message should explain the changes and reference the *issue* addressed by your code.
   Your pull request will be reviewed by one of the other team members.
   Pull requests should never be merged by the author of the contribution, but by another team member.
   Merge conflicts or errors reported by travis should be resolved by the original author before the request is merged. 


The issue tracker
-----------------

Please try to avoid duplicates of issues. If you encounter duplicated issues, please close all of them except 
one, reference the closed issues in the one that is left open and add missing information from the closed issues 
(if necessary) to the remaining issue.

Assign meaningful tags to newly crated issues and if possible assign them to milestones.


Reviewing pull requests
-----------------------

Every code (even small contributions from core developers) should be added to the project via pull requests.
Before reviewing a pull request it should pass all tests on travis-ci.
Each pull request that passes all builds and tests should be reviewed by at least one of the core developers.
If a contribution is rather complex or leads to significant API changes, the respective pull request should be 
reviewed by two other developers.
In such cases the first reviewer or the contributor should request a second review in a comment.


Testing
-------
   
* Unit test can be found in the `test` sub directory.

* Provide a unit test for every class, method or function. Please try to cover at least the most 
  important corner cases such as triggering of exceptions or missing default parameters.

* Please make sure that all tests pass before merging/sending pull requests.


Code style
----------

* Please stick to the [PEP8 code conventions](http://legacy.python.org/dev/peps/pep-0008/).

* Method, function, parameter and local variable names are written in *snake_case*. 
  Class names are written in *CamelCase*.

* Docstrings should be provided as [sphinxy info fields](http://sphinx-doc.org/domains.html#info-field-lists).

* Some IDEs such as [PyCharm](http://www.jetbrains.com/pycharm/) can help you to stick to the code and docstring 
  conventions.

* Try to avoid method and attribute names with single leading underscore. Prefer the use getters and setters with 
  @property decorators in combination with leading double underscore attribute names over public attributes for main
  API classes.

* In doubt just look at some existing files and adjust your code style and naming scheme accordingly.
