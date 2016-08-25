# -*- coding: utf-8 -*-

def phrase_index(sentence, phrase):
  '''
  Returns the start and end index of phrase (first instance) if it exists in
  sentence.

    ex: >>> phrase_index('the quick brown fox jumps over the lazy dog',
                         'brown fox jumps')
        (2, 4)
  '''
  # todo: use nltk parser instead of split?
  index = sentence.find(phrase)
  if index >= 0:
    if index == 0:
      start = 0
    else:
      # len happens to be same as index due to offset (index starts from 0)
      start = len(sentence[0:index-1].split(' '))
    wc_phrase = len(phrase.split(' '))
    end = start + wc_phrase - 1  # -1 so we don't double count first word
    return (start, end)
  return None
