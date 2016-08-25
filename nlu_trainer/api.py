# -*- coding: utf-8 -*-
'''
Interface for `NluTrainer`.
'''
import yaml


class NluTrainer(object):

  def train_set(self, dataset):
    for text, intent, entities in dataset:
      self.train(text, intent, yaml.load(entities))
    self.update()


  def add_intent(self, intent):
    '''
    Adds intent.
    '''
    raise NotImplementedError()


  def add_entity(self, entity):
    '''
    Adds entity.
    '''
    raise NotImplementedError()


  def add_synonyms(self, synonyms):
    '''
    Specify a set of words as synonyms.

      ex: add_synonyms(('form', 'letters', ...))
    '''
    raise NotImplementedError()


  def train(self, text, intent, entities):
    '''
    Associates `text` with the `intent` and describe where the known entities
    are.

      ex: train('what is a loggerhead turtle', 'define',
                {'animal': 'loggerhead turtle'})
    '''
    raise NotImplementedError()


  def predict(self, text):
    '''
    Predict the intent, entities, and score when given text.

      ex: >>> predict('what is a bengal tiger')
          { 'text': 'what is a bengal tiger',
            'intent': 'define',
            'entities": {'animal': 'bengal tiger'},
            'score': 0.9408 }
    '''
    raise NotImplementedError()


  def update(self):
    '''
    Update the system with the latest trained data.
    '''
    raise NotImplementedError()
