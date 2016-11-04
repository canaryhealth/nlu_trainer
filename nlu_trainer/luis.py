# -*- coding: utf-8 -*-
'''
Driver for Microsoft Language Understanding Intelligent Service (LUIS) API.
'''
import json
import os
import time

from aadict import aadict
import asset
import morph
from pyswagger import SwaggerApp
from pyswagger.contrib.client.requests import Client
from pyswagger.primitives import SwaggerPrimitive
from pyswagger.primitives._int import validate_int, create_int
from pyswagger.utils import jp_compose
from requests.exceptions import HTTPError

from . import util
from .api import NluTrainer
from .duration import asdur


ENTITY_POST       = 'entities - Create Entity Extractor'
PB_ENTITY_POST    = 'prebuilts - Add Prebuilt Entity Extractor'
EXAMPLE_POST      = 'example - Add Label'
INTENT_POST       = 'intents - Create Intent Classifier'
PHRASELIST_POST   = 'phraselists - Create New Dictionary'
PREDICT_GET       = 'predict - get Trained Model Predictions'
UPDATE_POST       = 'train - Train'
UPDATE_GET        = 'train - Training Status'

ENTITIES_GET      = 'entities - get Entity Infos'
PB_ENTITIES_GET   = 'prebuilts - get Prebuilt Infos'
ENTITY_GET        = 'entities - get Entity Info'
PB_ENTITY_GET     = 'prebuilts - get Prebuilt Info'
ENTITY_DELETE     = 'entities - delete Entity Model'
PB_ENTITY_DELETE  = 'prebuilts - delete Prebuilt Model'
EXAMPLE_DELETE    = 'examples - delete Example Labels'
EXAMPLES_GET      = 'examples - Review Labeled Utterances'
INTENT_DELETE     = 'intents - delete Intent Model'
INTENTS_GET       = 'intents - get Intent Infos'
PHRASELISTS_GET   = 'phraselists - get Phraselists'

# todo: geography, encyclopedia, and datetime has more children
BUILTIN_ENTITIES  = ['number', 'ordinal', 'temperature', 'dimension', 'money',
                     'age', 'geography', 'encyclopedia', 'datetime']

#------------------------------------------------------------------------------
class LuisTrainer(NluTrainer):
  # TODO: formalize/abstract return values

  def __init__(self, settings):
    self.settings = settings
    # create a customized primitive factory for int because library
    # impractically chooses not to set default (b/t int32 vs int64) b/c
    # the Swagger/OpenAPI spec doesn't
    # https://github.com/mission-liao/pyswagger/issues/65
    int_factory = SwaggerPrimitive()
    int_factory.register('integer', '', create_int, validate_int)
    int_factory.register('integer', None, create_int, validate_int)
    self.app = SwaggerApp.load(
      os.path.join(os.path.dirname(os.path.realpath(__file__)),
                   'luis_api-1.0.swagger.json'),
      prim=int_factory)
    self.app.prepare()
    self.client = Client()


  def _request(self, op, body=None):
    time.sleep(asdur(self.settings.req_throttle))
    params = dict(appId = self.settings.app_id)
    if body:
      params.update(body)
    req, res = self.app.op[op](**params)
    req.header['Ocp-Apim-Subscription-Key'] = self.settings.sub_key
    response = self.client.request((req, res))

    ret = None
    if response.raw:
      ret = json.loads(response.raw)

    # pyswagger requires "requests" library... but roll their own request/
    # response object. copying raise_for_status() functionality...
    http_error_msg = ''
    if 400 <= response.status < 500:
      http_error_msg = '%s Client Error: %s' % (response.status,
                                                ret['error']['message'])
    elif 500 <= response.status < 600:
      http_error_msg = '%s Server Error: %s' % (response.status,
                                                ret['error']['message'])
    if http_error_msg:
      raise HTTPError(http_error_msg, response=response)

    return ret


  def _sanitize(self, text):
    '''
    Emulates behavior where LUIS lowercases the input and pads spaces for
    "special" chars.
    '''
    CHARS = '"\',.-()'  # based on observation and may not be exhaustive
    if not isinstance(text, (str, unicode)):
      text = unicode(text)
    text = text.lower().strip()
    # todo: improve this poor man's way of tokenizing
    t = text.split(' ')
    for idx, val in enumerate(t):
      for c in CHARS:
        if c in val:
          val = val.replace(c, ' %s ' % c)  # pad c with spaces
          t[idx] = val.split()
    return ' '.join(morph.flatten(t))


  def add_intent(self, intent):
    return self._request(INTENT_POST,
                         dict(intentModel = {'Name': intent}))


  def add_entity(self, entity):
    if entity in BUILTIN_ENTITIES:
      # returning prebuilt entity id to normalize response
      return self._request(PB_ENTITY_POST,
                           dict(prebuiltExtractorNames = entity))[0]['id']
    return self._request(ENTITY_POST,
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

    return self._request(EXAMPLE_POST,
                         dict(exampleLabel = {'ExampleText': text,
                                              'SelectedIntentName': intent,
                                              'EntityLabels': labels}))


  def predict(self, text):
    intent = None
    score = None
    entities = {}

    body = aadict.d2ar(self._request(PREDICT_GET, dict(example = text)))
    for i in body.IntentsResults:
      # returns the intent with the highest score
      if i.score > score:
        score = i.score
        intent = i.Name
    for e in body.EntitiesResults:
      entities[e.name] = e.word

    return (body.utteranceText, intent, entities, score)


  def update(self):
    self._request(UPDATE_POST)
    while True:
      time.sleep(asdur(self.settings.status_polling_interval))
      status = [ i['Details']['Status'] for i in self._request(UPDATE_GET) ]
      if 'In progress' not in set(status):
        break


  def get_update(self):
    return self._request(UPDATE_GET)

  #----------------------------------------------------------------------------
  # todo: should we expose the following in the api interface?

  def get_intents(self):
    return self._request(INTENTS_GET)

  def delete_intent(self, intent_id):
    return self._request(INTENT_DELETE, dict(intentId=intent_id))


  def get_entities(self):
    return self._request(ENTITIES_GET) + self._request(PB_ENTITIES_GET)

  # untested/not currently used
  # def get_entity(self, entity_id):
  #   self._request(ENTITY_GET, dict(entityId=entity_id))
  #   self._request(PB_ENTITY_GET, dict(prebuiltId=entity_id))

  def delete_entity(self, entity_id):
    try:
      return self._request(ENTITY_DELETE, dict(entityId=entity_id))
    except HTTPError as e:
      if 'prebuilt' in e.message:
        return self._request(PB_ENTITY_DELETE, dict(prebuiltId=entity_id))
      raise e


  def get_examples(self):
    return self._request(EXAMPLES_GET, dict(skip=0, count=10))

  def delete_example(self, example_id):
    return self._request(EXAMPLE_DELETE, dict(exampleId=example_id))


  def get_synonyms(self):
    pass
