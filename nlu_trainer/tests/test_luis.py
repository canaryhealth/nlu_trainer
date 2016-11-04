# -*- coding: utf-8 -*-
import ConfigParser
import os
import unittest

from aadict import aadict
import asset


# TODO: this is more of a sanity check than a proper unittest. we don't have
#       a way to independently verify the results directly without going thru
#       the api. there also isn't an easy way to reset the luis env/app.


class LuisApiTestCase(unittest.TestCase):

  def setUp(self):
    super(LuisApiTestCase, self).setUp()

    inifile =  os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            '../../test.ini')
    cp = ConfigParser.RawConfigParser()
    cp.read(inifile)
    settings = aadict(cp.items('nlu_trainer'))
    self.settings = settings
    self.trainer = asset.symbol(settings.driver)(settings)


  def test_intents(self):
    # test get all
    self.assertItemsEqual(
      [ x['name'] for x in self.trainer.get_intents() ],
      [ 'None' ]
    )
    # test add
    a_id = self.trainer.add_intent('aaa')
    b_id = self.trainer.add_intent('bbb')
    self.assertItemsEqual(
      [ x['name'] for x in self.trainer.get_intents() ],
      [ 'None', 'aaa', 'bbb' ]
    )
    # test delete
    self.trainer.delete_intent(a_id)
    self.trainer.delete_intent(b_id)
    self.assertItemsEqual(
      [ x['name'] for x in self.trainer.get_intents() ],
      [ 'None' ]
    )


  def test_entities(self):
    # test get all
    self.assertEquals(len(self.trainer.get_entities()), 0)
    # test add
    c_id = self.trainer.add_entity('ccc')
    d_id = self.trainer.add_entity('ddd')
    num_id = self.trainer.add_entity('number')
    self.assertItemsEqual(
      self.trainer.get_entities(),
      [ dict(id = c_id, name = 'ccc', type = 'Entity Extractor'),
        dict(id = d_id, name = 'ddd', type = 'Entity Extractor'),
        dict(id = num_id, name = 'number', type = 'Prebuilt Entity Extractor'),
      ]
    )
    # test delete
    self.trainer.delete_entity(c_id)
    self.trainer.delete_entity(d_id)
    self.trainer.delete_entity(num_id)
    self.assertEquals(len(self.trainer.get_entities()), 0)


  def test_examples(self):
    # test get all
    self.assertEquals(len(self.trainer.get_intents()), 1)
    self.assertEquals(len(self.trainer.get_entities()), 0)
    self.assertEquals(len(self.trainer.get_examples()), 0)
    # test train
    i_id = self.trainer.add_intent('iii')
    e_id = self.trainer.add_entity('eee')
    ex = self.trainer.train('this is an-example', 'iii',
                            { 'eee': 'an-example'})
    self.trainer.update()
    # test predict
    # t, i, e, s =  self.trainer.predict('this is an-example')
    # self.assertEquals(t, 'this is an-example')
    # self.assertEquals(i, 'iii')
    # self.assertEquals(e, {'eee': 'an-example'})
    # self.assertEquals(s, 1)
    # test delete
    self.trainer.delete_intent(i_id)
    self.trainer.delete_entity(e_id)
    self.trainer.delete_example(ex['ExampleId'])
    self.assertEquals(len(self.trainer.get_intents()), 1)
    self.assertEquals(len(self.trainer.get_entities()), 0)
    self.assertEquals(len(self.trainer.get_examples()), 0)


  # def test_synonyms(self):
  #   pass
