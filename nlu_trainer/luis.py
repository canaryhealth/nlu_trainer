# -*- coding: utf-8 -*-
'''
Driver for Microsoft Language Understanding Intelligent Service (LUIS) API.
'''
import asset
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose

from .api import NluTrainer


ENTITY_POST     = 'entities - Create Entity Extractor'
EXAMPLE_POST    = 'example - Add Label'
INTENT_POST     = 'intents - Create Intent Classifier'
PHRASELIST_POST = 'phraselists - Create New Dictionary'
PREDICT_GET     = 'predict - get Trained Model Predictions'


class LuisTrainer(NluTrainer):

  def __init__(self, settings):
    self.sub_key = settings.sub_key
    self.app_id  = settings.app_id
    # todo: fix path
    self.app = App._create_('nlu_trainer/luis_api-1.0.swagger.json')
    self.client = Client()


  def _request(self, op, body):
    params = dict(appId = self.app_id)
    params.update(body)
    req, res = self.app.op[op](**params)
    req.header['Ocp-Apim-Subscription-Key'] = self.sub_key
    return self.client.request((req, res))


  def add_intent(self, intent):
    response = self._request(INTENT_POST,
                             dict(intentModel = {'Name': intent}))
    if response.status != 201:
      pass # todo: log


  def add_entity(self, entity):
    response = self._request(ENTITY_POST,
                             dict(hierarchicalModel = {'Name': entity}))
    if response.status != 201:
      pass # todo: log


  def add_synonyms(self, synonyms):
    pass


  def train(self, text, intent, entities):
    # labels = []
    # for t, e in entities:
    #   labels.append(dict(EntityType = t,
    #                      StartToken =,
    #                      EndToken = ))

    # self.client.request(
    #   self.app.resolve(jp_compose(ENTITY_URL)).post(
    #     appId = self.app_id,
    #     ExampleText = text,
    #     SelectedIntentName = intent
    #     EntityLabels = labels
    #   )
    # )
    pass


  def predict(self, utterance):
    pass
