# -*- coding: utf-8 -*-
'''
Interface for `NluTrainer`.
'''
import unittest

import yaml


class NluTrainer(object):
  # todo: properly handle locale. currently ignores value

  def train_set(self, dataset):
    '''
    Trains dataset with NLU.
    '''
    intent_list = []
    entities_list = []
    for locale, text, intent, entities in dataset:
      if intent not in intent_list:
        intent_list.append(intent)
        self.add_intent(intent)
      entities = yaml.load(entities) or {}
      for entity in entities.keys():
        if entity not in entities_list:
          entities_list.append(entity)
          self.add_entity(entity)
      self.train(text, intent, entities)
    self.update()


  def predict_set(self, dataset):
    results = []
    try:
      for locale, text in dataset:
        # TODO: the entities returned by LUIS would be sanitized and not match
        #       the text
        results.append((locale,) + self.predict(text))
    finally:
      return results


  def test_set(self, dataset):
    '''
    Tests dataset against NLU.
    '''
    trainer = self

    class TestNluMeta(type):
      def __new__(mcs, name, bases, dict):
        def gen_test(trainer, text, expected_intent, expected_entities):
          def test_prediction(self):
            text2, intent, entities, score = trainer.predict(text)
            self.assertEqual(text2, text.lower())
            self.assertEqual(intent, expected_intent)
            if expected_entities:
              self.assertEqual(
                entities,
                { k: trainer._sanitize(v) for k, v in expected_entities.items() })
            if trainer.settings.score_threshold:
              self.assertGreaterEqual(score,
                                      float(trainer.settings.score_threshold))
          return test_prediction
        for locale, text, intent, entities in dataset:
          test_name = "test_%s" % text.replace(' ', '_')
          dict[test_name] = gen_test(trainer, text, intent, yaml.load(entities))
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
