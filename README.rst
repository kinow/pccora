PCCORA
======

PC-CORA parser for Python. Supports the format described here
https://badc.nerc.ac.uk/data/ukmo-rad-hires/pc-coradata.html (2015-12-05).

This format is used for [radiosonde data](https://badc.nerc.ac.uk/data/ukmo-rad-hires/). According to Wikipedia,

"A radiosonde (Sonde is French and German for probe) is a battery-powered telemetry instrument package carried into the
atmosphere usually by a weather balloon that measures various atmospheric parameters and transmits them by radio to a
ground receiver."

History
-------

I was asked by a co-worker to look at some Python code with a PC-CORA parser. However, he also needed some further
work on finding these files and outputting the contents as CSV. Decided to write a module for PC-CORA inspiredby the
original script [1], using Python3, OO and packing as a Python package to be distributed to the
`PYPI <https://pypi.python.org/pypi>`.

[1] https://github.com/vnoel/pycode/blob/master/pccora.py

Example
-------

    >>> from pccora import PCCORAParser
    >>> pccora_parser = PCCORAParser()
    >>> pccora_parser.parse_file('./123456789.EDT')
    >>> print(pccora_parser.get_header())
    >>> print(pccora_parser.get_identification())
    >>> print(pccora_parser.get_data())

Requirements
------------

Python 2 or Python 3, and the `construct library <https://github.com/construct/construct>`.

License
-------

Licensed under the MIT License.
