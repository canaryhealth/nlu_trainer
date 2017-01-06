# -*- coding: utf-8 -*-
'''
Interface for `NluTrainer`.
'''
import unittest

from requests.exceptions import HTTPError
import yaml


class NluTrainer(object):
  # todo: properly handle locale. currently ignores value

  def train_set(self, app_id, dataset):
    '''
    Trains dataset with NLU.
    '''
    intent_list = []
    entities_list = []
    for locale, text, intent, entities in dataset:
      if intent not in intent_list:
        intent_list.append(intent)
        try:
          self.add_intent(app_id, intent)
        except HTTPError as e:
          if 'already exists' not in e.message:
            raise e
      entities = yaml.load(entities) or {}
      for entity in entities.keys():
        if entity not in entities_list:
          entities_list.append(entity)
          try:
            self.add_entity(app_id, entity)
          except HTTPError as e:
            if not ('already contains' in e.message  # prebuilt-entities
                    or 'already exists' in e.message):  # entities
              raise e
      self.train(app_id, text, intent, entities)
    self.update(app_id)


  def predict_set(self, app_id, dataset):
    results = []
    try:
      for locale, text in dataset:
        # TODO: the entities returned by LUIS would be sanitized and not match
        #       the text
        results.append((locale,) + self.predict(app_id, text))
    finally:
      return results


  def test_set(self, app_id, dataset):
    '''
    Tests dataset against NLU.
    '''
    trainer = self

    class TestNluMeta(type):
      def __new__(mcs, name, bases, dict):
        def gen_test(trainer, text, expected_intent, expected_entities):
          def test_prediction(self):
            text2, intent, entities, score = trainer.predict(app_id, text)
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
  def add_intent(self, app_id, intent):
    '''
    Adds intent.
    '''
    raise NotImplementedError()


  def add_entity(self, app_id, entity):
    '''
    Adds entity.
    '''
    raise NotImplementedError()


  def add_synonyms(self, app_id, synonyms):
    '''
    Specify a set of words as synonyms.

      ex: add_synonyms(('form', 'letters', ...))
    '''
    raise NotImplementedError()


  def train(self, app_id, text, intent, entities):
    '''
    Associates `text` with the `intent` and describe where the known entities
    are.

      ex: train('what is a loggerhead turtle', 'define',
                { animal: loggerhead turtle })
    '''
    raise NotImplementedError()


  def predict(self, app_id, text):
    '''
    Predict the intent, entities, and score when given text.

      ex: >>> predict('what is a bengal tiger')
          { 'text': 'what is a bengal tiger',
            'intent': 'define',
            'entities": { animal: bengal tiger},
            'score': 0.9408 }
    '''
    raise NotImplementedError()


  def update(self, app_id):
    '''
    Update the system with the latest trained data.
    '''
    raise NotImplementedError()
