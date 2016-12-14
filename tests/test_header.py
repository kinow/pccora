import unittest

from construct import *
import pccora

class TestHeader(unittest.TestCase):

    def test_header(self):
        h = pccora.pccora.pccora_header
        struct = h.parse(b'(C) copytest        ^@^@^@^@<C4>^@<97>^_<D1>^B^L^@^B^@(^@^B^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^A^@^D^@^B^@9^A<99>^C3!^D^@^@^D=^@^@<80>^@^@^@^@<B4>^A')
        self.assertEqual('(C) copytest', struct['copyright'].strip())
