# -*- coding: utf-8 -*-
import unittest

from .. import util

class TestUtil(unittest.TestCase):

  def test_phrase_index(self):
    self.assertEqual(
      util.phrase_index('the quick brown fox jumps over the lazy dog',
                        'the'),
      (0, 2)
    )
    self.assertEqual(
      util.phrase_index('the quick brown fox jumps over the lazy dog',
                        'brown fox jumps'),
      (10, 24)
    )
    self.assertIsNone(
      util.phrase_index('the quick brown fox jumps over the lazy dog',
                        'cheshire cat')
    )
    self.assertEqual(
      util.phrase_index('99 bottles of beer on the wall',
                        '99'),
      (0, 1)
    )
    self.assertEqual(
      util.phrase_index(
        'the term co.payment can be abbreviated as co.pay if you like',
        'co.pay'),
      (42, 47)
    )
    self.assertEqual(
      util.phrase_index(
        'xx  xx  xx registered nurses  xxxxx registered nurse xx xx xx xxxx xx xxxx',
        'registered nurse'),
      (36, 51)
    )
