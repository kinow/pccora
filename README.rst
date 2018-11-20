PCCORA
======

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.1163385.svg
   :target: https://doi.org/10.5281/zenodo.1163385

.. image:: https://travis-ci.org/kinow/pccora.svg?branch=master
   :target: https://travis-ci.org/kinow/pccora

.. image:: https://coveralls.io/repos/github/kinow/pccora/badge.svg?branch=master
   :target: https://coveralls.io/github/kinow/pccora?branch=master


PC-CORA parser for Python. Supports the format described at `<https://badc.nerc.ac.uk/data/ukmo-rad-hires/pc-coradata.html>`_ (accessed at 2015-12-05).

This format is used for `radiosonde data <https://badc.nerc.ac.uk/data/ukmo-rad-hires/>`_.

    A radiosonde (Sonde is French and German for probe) is a battery-powered telemetry instrument package carried into the atmosphere usually by a weather balloon that measures various atmospheric parameters and transmits them by radio to a ground receiver. (Wikipedia)

This format is produced by old `Vaisala <http://www.vaisala.com>`_ equipments. Newer data is probably available in the NetCDF.

History
-------

I was asked by a co-worker to look at some Python code with a PC-CORA parser.
This co-worker also needed further analysis and processing, involving some
data being created as CSV, netCDF, or plotted.

I decided to write a module for PC-CORA inspired by the
`original script <https://github.com/vnoel/pycode/blob/39bac18dc41497a5a00cbecd6b81ddf205736615/pccora.py>`_,
but using Python3, OO, and packaging as a Python package to be distributed
to the `PYPI <https://pypi.org/project/pccora/>`_.

This way we could use it in scripts, or other internal applications. And it
would also be easier for others to find it and re-use.

The code in this repository was used on a `Doctoral Thesis
<https://refubium.fu-berlin.de/handle/fub188/22207>`_ published in 2018,
about radiosonde, GCOS, radio occultation, and weather prediction.

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

There are datasets available at the `CEDA website
<http://catalogue.ceda.ac.uk/>`_ (Centre for Environmental Data Archival),
however, access is restricted.

`NOAA's ESRL <http://www.esrl.noaa.gov>`_ (Earth System Research Laboratory)
has an FTP server with some data in the the old PC-CORA sounding data format.
Just search for FTP for instructions on how to access the Physical Sciences
Division FTP server. Some valid files can be found at
`/psd3/cruises/AERO_1999/RHB/balloon/Raw` (accessed 2016-01-17).

Requirements
------------

Python 3.6 or superior, and the `construct library
<https://github.com/construct/construct>`_ are the minimum requirements.

Installation
------------

    pip install pccora

Or, to use the bleeding edge version, git clone this repository, and have a
look at the scripts folders for an example how to use the module from
within a local folder. You may have to uninstall the pip module first.

    python setup.py install

The PYPI URL is `<https://pypi.python.org/pypi/pccora>`_.

License
-------

Licensed under the MIT License.
