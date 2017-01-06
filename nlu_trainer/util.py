# -*- coding: utf-8 -*-
import re

def phrase_index(sentence, phrase):
  '''
  Returns the start and end index of phrase (first instance) if it exists in
  sentence.

    ex: >>> phrase_index('the quick brown fox jumps over the lazy dog',
                         'brown fox jumps')
        (10, 24)
  '''
  phrase = str(phrase)  # in case phrase is a number
  m = re.match(r'(.*?)\b'+re.escape(phrase)+r'\b', sentence)
  if m:
    # group 0 and 1 returns the match with and without the phrase respectively
    l = len(m.group(1))
    return (l, l+len(phrase)-1)
  return None


def phrase_pos(sentence, phrase):
  '''
  Returns the start and end position of phrase (first instance) if it exists in
  sentence.

    ex: >>> phrase_index('the quick brown fox jumps over the lazy dog',
                         'brown fox jumps')
        (2, 5)
  '''
  phrase = str(phrase)  # in case phrase is a number
  s_tok = sentence.split()
  p_tok = phrase.split()
  p_len = len(p_tok)

  # get all indices where s_tok[i] matches p_tok[0]
  indices = [ i for i, x in enumerate(s_tok) if x == p_tok[0] ]
  for i in indices:
    if s_tok[i : i+p_len] == p_tok:
      return i, i+p_len
  return None
