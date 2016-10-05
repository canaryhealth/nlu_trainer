# -*- coding: utf-8 -*-

def phrase_index(sentence, phrase):
  '''
  Returns the start and end index of phrase (first instance) if it exists in
  sentence.

    ex: >>> phrase_index('the quick brown fox jumps over the lazy dog',
                         'brown fox jumps')
        (10, 24)
  '''
  phrase = str(phrase)  # in case phrase is a number
  index = sentence.find(phrase)
  if index >= 0:
    return (index, index+len(phrase)-1)
  return None
