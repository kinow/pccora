"""
PCCORA - A PC-CORA binary parser in Python

Homepage:
    https://github.com/kinow/pccora/wiki

Hands-on example:
    >>> from pccora import *
    >>> pccora_parser = PCCORAParser()
    >>> pccora_parser.parse_file('./123456789.EDT')
    >>> print(pccora_parser.get_header())
    >>> print(pccora_parser.get_identification())
    >>> print(pccora_parser.get_data())
"""

from pccora.pccora import PCCORAParser
from pccora.version import version, version_string as __version__

#===============================================================================
# Metadata
#===============================================================================
__author__ = "Bruno P. Kinoshita <brunodepaulak@yahoo.com.br>"

#===============================================================================
# exposed names
#===============================================================================
__all__ = [
    'PCCORAParser'
]
