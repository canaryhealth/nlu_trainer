# -*- coding: utf-8 -*-
'''
Driver for Microsoft Language Understanding Intelligent Service (LUIS) API.
'''
import json

from aadict import aadict
import asset
from pyswagger import SwaggerApp
from pyswagger.contrib.client.requests import Client
from pyswagger.primitives import SwaggerPrimitive
from pyswagger.primitives._int import validate_int, create_int
from pyswagger.utils import jp_compose

from . import util
from .api import NluTrainer


ENTITY_POST     = 'entities - Create Entity Extractor'
EXAMPLE_POST    = 'example - Add Label'
INTENT_POST     = 'intents - Create Intent Classifier'
PHRASELIST_POST = 'phraselists - Create New Dictionary'
PREDICT_GET     = 'predict - get Trained Model Predictions'
UPDATE_POST     = 'train - Train'


class LuisTrainer(NluTrainer):

  def __init__(self, settings):
    self.settings = settings
    # create a customized primitive factory for int because library
    # impractically chooses not to set default (b/t int32 vs int64) b/c
    # the Swagger/OpenAPI spec doesn't
    # https://github.com/mission-liao/pyswagger/issues/65
    int_factory = SwaggerPrimitive()
    int_factory.register('integer', '', create_int, validate_int)
    int_factory.register('integer', None, create_int, validate_int)
    # todo: fix path
    self.app = SwaggerApp.load('nlu_trainer/luis_api-1.0.swagger.json',
                               prim=int_factory)
    self.app.prepare()
    self.client = Client()


  def _request(self, op, body=None):
    params = dict(appId = self.settings.app_id)
    if body:
      params.update(body)
    req, res = self.app.op[op](**params)
    req.header['Ocp-Apim-Subscription-Key'] = self.settings.sub_key
    response = self.client.request((req, res))
    if response.status != 201:
      pass  # todo: implement error handling
    return response


  def add_intent(self, intent):
    response = self._request(INTENT_POST,
                             dict(intentModel = {'Name': intent}))


  def add_entity(self, entity):
    response = self._request(ENTITY_POST,
                             dict(hierarchicalModel = {'Name': entity}))


  def add_synonyms(self, synonyms):
    pass


  def train(self, text, intent, entities):
    labels = []
    for t, e in entities.items():
      index = util.phrase_index(text, e)
      if index:
        labels.append({'EntityType': t,
                       'StartToken': index[0],
                       'EndToken': index[1]})

    response = self._request(EXAMPLE_POST,
                             dict(exampleLabel = {'ExampleText': text,
                                                  'SelectedIntentName': intent,
                                                  'EntityLabels': labels}))


  def predict(self, text):
    intent = None
    score = None
    entities = {}

    response = self._request(PREDICT_GET, dict(example = text))
    if response.status == 200:
      body = aadict.d2ar(json.loads(response.raw))
      for i in body.IntentsResults:
        # returns the intent with the highest score
        if i.score > score:
          score = i.score
          intent = i.Name
      for e in body.EntitiesResults:
         entities[e.name] = e.word

    return (text, intent, entities, score)


  def update(self):
    response = self._request(UPDATE_POST)
