import unittest

from construct import *
import pccora

class TestHeader(unittest.TestCase):

    def test_header(self):
        h = pccora.pccora.pccora_header
        struct = h.parse()
        self.assertEqual('copytest', struct['copyright'])
