# -*- coding: utf-8 -*-
import unittest

from .. import util

class TestUtil(unittest.TestCase):

  def test_phrase_index(self):
    self.assertEqual(
      util.phrase_index('the quick brown fox jumps over the lazy dog',
                        'the'),
      (0, 0)
    )
    self.assertEqual(
      util.phrase_index('the quick brown fox jumps over the lazy dog',
                        'brown fox jumps'),
      (2, 4)
    )
    self.assertIsNone(
      util.phrase_index('the quick brown fox jumps over the lazy dog',
                        'cheshire cat')
    )
