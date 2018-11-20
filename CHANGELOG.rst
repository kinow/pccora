=========
Changelog
=========

0.3
===

* Remove unused code
* Updated setup.py to handle optional dependencies for scripts under Linux/Win
* Fixed static analysis issues
* Updated travis-ci to check syntax, run tests, and use xenial dist
* Fixed imports
* Removed sys.path hacking from scripts (now users must install pccora)
* Fixed one bug where rsigkey would not have the correct values after parse
* Fixed several issues when None was compared with ==/!=, instead of is/is not
* Reviewed this Changelog file comparing with git log
* Removed unused/unnecessary version.py

0.2
===

* Fixed construct build process (0.0.1 was tested only with parse in mind)
* Added PIP dependencies netCDF4, numpy

0.1
===

* First release working after tests with multiple real radiosonde data files
* Fixed several inconsistencies, and parsing issues
* Finished initial project structure

0.0.1
===

* Initial release, using `construct <https://github.com/construct/construct>`.
