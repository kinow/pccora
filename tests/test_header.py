import unittest
from pccora import *

class TestHeader(unittest.TestCase):

    def test_header(self):
        h = pccora_header
        struct = h.parse()
        self.assertEqual('copytest', struct['copyright'])