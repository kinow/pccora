PCCORA
======

.. image:: https://travis-ci.org/kinow/pccora.svg?branch=master
:target: https://travis-ci.org/kinow/pccora

.. image:: https://coveralls.io/repos/github/kinow/pccora/badge.svg?branch=master
:target: https://coveralls.io/github/kinow/pccora?branch=master


PC-CORA parser for Python. Supports the format described here `https://badc.nerc.ac.uk/data/ukmo-rad-hires/pc-coradata.html` (accessed at 2015-12-05).

This format is used for `radiosonde data https://badc.nerc.ac.uk/data/ukmo-rad-hires/`. According to Wikipedia,

"A radiosonde (Sonde is French and German for probe) is a battery-powered telemetry instrument package carried into the atmosphere usually by a weather balloon that measures various atmospheric parameters and transmits them by radio to a ground receiver."

This format is produced by old `Vaisala http://www.vaisala.com` equipments. Newer data is probably available in the NetCDF.

History
-------

I was asked by a co-worker to look at some Python code with a PC-CORA parser. However, he also needed some further work on finding these files and outputting the contents as CSV. Decided to write a module for PC-CORA inspired by the original script [1], using Python3, OO and packing as a Python package to be distributed to the `PYPI https://pypi.python.org/pypi`.

[1] https://github.com/vnoel/pycode/blob/master/pccora.py

Example
-------

    >>> from pccora import PCCORAParser
    >>> pccora_parser = PCCORAParser()
    >>> pccora_parser.parse_file('./123456789.EDT')
    >>> print(pccora_parser.get_header())
    >>> print(pccora_parser.get_identification())
    >>> print(pccora_parser.get_data())

Obtaining Data
--------------

There are datasets available at the `CEDA website http://catalogue.ceda.ac.uk/` (Centre for Environmental Data Archival), however, access is restricted.

`NOAA's ESRL http://www.esrl.noaa.gov` (Earth System Research Laboratory) has an FTP server with some data in the the old PC-CORA sounding data format. Just search for FTP for instructions on how to access the Physical Sciences Division FTP server. Some valid files can be found at `/psd3/cruises/AERO_1999/RHB/balloon/Raw` (checked on 2016-01-17).

Requirements
------------

Python 2 or Python 3, and the `construct library https://github.com/construct/construct`.

Installation
------------

    pip install pccora

Or, to use the bleeding edge version, git clone this repository, and have a look at the scripts folders for an example how to use the module from within a local folder. You may have to uninstall the pip module first.

The PYPI URL is https://pypi.python.org/pypi/pccora.

License
-------

Licensed under the MIT License.
