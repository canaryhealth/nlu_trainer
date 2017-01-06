#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
CLI to train/test Natural Language Understanding system.
'''
import argparse
import ConfigParser
import csv
import sys

from aadict import aadict
import asset


TRAIN   = 'train'
TEST    = 'test'
PURGE   = 'purge'
PREDICT = 'predict'

def main(args=None):
  cli = argparse.ArgumentParser(
    description=__doc__,
    epilog='ex: python cli.py train settings.ini -d train_set.csv')
  cli.add_argument('command', metavar='COMMAND',
                   help='{ train | test | predict | purge }',
                   choices=(TRAIN, TEST, PREDICT, PURGE))
  cli.add_argument('config', metavar='CONFIG', help='config file with settings')
  cli.add_argument('-d', '--dataset', metavar='DATASET', help='dataset file')

  options  = cli.parse_args(args=args)
  cp = ConfigParser.RawConfigParser()
  cp.read(options.config)
  settings = aadict(cp.items('nlu_trainer'))

  trainer = asset.symbol(settings.driver)(settings)
  predictions = []
  if options.command in (TRAIN, TEST, PREDICT):
    with open(options.dataset, 'rb') as csv_file:
      r = csv.reader(csv_file)
      if options.command == TRAIN:
        trainer.train_set(settings.app_id, r)
      elif options.command == TEST:
        trainer.test_set(settings.app_id, r)
      elif options.command == PREDICT:
        predictions = trainer.predict_set(settings.app_id, r)
  elif options.command == PURGE:
    purge(trainer, settings)

  if options.command == PREDICT:
    w = csv.writer(sys.stdout)
    w.writerows(predictions)


def purge(trainer, settings):
  # delete examples
  for e_id in [ x['exampleId'] for x in trainer.get_examples(settings.app_id) ]:
    trainer.delete_example(settings.app_id, e_id)
  # delete intent
  for i in trainer.get_intents(settings.app_id):
    if i['name'] != 'None':
      trainer.delete_intent(settings.app_id, i['id'])
  # delete entities
  for e_id in [ x['id'] for x in trainer.get_entities(settings.app_id) ]:
    trainer.delete_entity(settings.app_id, e_id)

  trainer.update(settings.app_id)

#------------------------------------------------------------------------------
main()
