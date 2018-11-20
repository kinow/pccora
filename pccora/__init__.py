"""
PCCORA - A PC-CORA binary parser in Python

Homepage:
    https://github.com/kinow/pccora/wiki

Hands-on example:
    >>> import os
    >>> from pccora import *
    >>> pccora_parser = PCCORAParser()
    >>> cur_dir = os.path.dirname(__file__)
    >>> in_file = os.path.join(cur_dir, "tests/93011809.21S")
    >>> pccora_parser.parse_file(in_file)
    >>> assert pccora_parser.get_header() is not None
    >>> assert pccora_parser.get_identification() is not None
    >>> assert pccora_parser.get_data() is not None
"""

from .pccora import PCCORAParser

# ===============================================================================
# Metadata
# ===============================================================================
__author__ = "Bruno P. Kinoshita <brunodepaulak@yahoo.com.br>"

# ===============================================================================
# exposed names
# ===============================================================================
__all__ = [
    'PCCORAParser'
]
