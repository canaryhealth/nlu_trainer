# -*- coding: utf-8 -*-
'''
Interface for `NluTrainer`.
'''
import time
import unittest

import yaml

from .duration import asdur


class NluTrainer(object):

  def train_set(self, dataset):
    '''
    Trains dataset with NLU.
    '''
    for text, intent, entities in dataset:
      self.train(text, intent, yaml.load(entities))
    self.update()


  def predict_set(self, dataset):
    results = []
    try:
      for text in dataset:
        # TODO: the entities returned by LUIS would be sanitized and not match
        #       the text
        results.append(self.predict(text))
    finally:
      return results


  def test_set(self, dataset):
    '''
    Tests dataset against NLU.
    '''
    trainer = self
    test_throttle = self.settings.test_throttle

    class TestNluMeta(type):
      def __new__(mcs, name, bases, dict):
        def gen_test(trainer, test_throttle,
                     text, expected_intent, expected_entities):
          def test_prediction(self):
            time.sleep(asdur(test_throttle))
            text2, intent, entities, score = trainer.predict(text)
            self.assertEqual(text2, text.lower())
            self.assertEqual(intent, expected_intent)
            self.assertEqual(
              entities,
              { k: trainer._sanitize(v) for k, v in expected_entities.items() })
            if trainer.settings.score_threshold:
              self.assertGreaterEqual(score,
                                      float(trainer.settings.score_threshold))
          return test_prediction
        for text, intent, entities in dataset:
          test_name = "test_%s" % text.replace(' ', '_')
          dict[test_name] = gen_test(trainer, test_throttle,
                                     text, intent, yaml.load(entities))
        return type.__new__(mcs, name, bases, dict)

    class TestNlu(unittest.TestCase):
      __metaclass__ = TestNluMeta

    tests = unittest.TestLoader().loadTestsFromTestCase(TestNlu)
    unittest.TextTestRunner().run(tests)

  #----------------------------------------------------------------------------
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
                { animal: loggerhead turtle })
    '''
    raise NotImplementedError()


  def predict(self, text):
    '''
    Predict the intent, entities, and score when given text.

      ex: >>> predict('what is a bengal tiger')
          { 'text': 'what is a bengal tiger',
            'intent': 'define',
            'entities": { animal: bengal tiger},
            'score': 0.9408 }
    '''
    raise NotImplementedError()


  def update(self):
    '''
    Update the system with the latest trained data.
    '''
    raise NotImplementedError()
