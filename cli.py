# -*- coding: utf-8 -*-
'''
CLI to train/test Natural Language Understanding system.
'''
import argparse
import ConfigParser
import csv

from aadict import aadict
import asset


TRAIN = 'train'
TEST  = 'test'
PURGE = 'purge'

def main(args=None):
  cli = argparse.ArgumentParser(
    description=__doc__,
    epilog='ex: python cli.py train settings.ini -d train_set.csv')
  cli.add_argument('command', metavar='COMMAND', help='{ train | test | purge }',
                   choices=(TRAIN, TEST, PURGE))
  cli.add_argument('config', metavar='CONFIG', help='config file with settings')
  cli.add_argument('-d', '--dataset', metavar='DATASET', help='dataset file')

  options  = cli.parse_args(args=args)
  cp = ConfigParser.RawConfigParser()
  cp.read(options.config)
  settings = aadict(cp.items('nlu_trainer'))

  trainer = asset.symbol(settings.driver)(settings)
  if options.command in (TRAIN, TEST):
    with open(options.dataset) as csv_file:
      r = csv.reader(csv_file)
      if options.command == TRAIN:
        trainer.train_set(r)
      elif options.command == TEST:
        trainer.test_set(r)
  elif options.command == PURGE:
    purge(trainer)


def purge(trainer):
  # delete examples
  for e_id in [ x['exampleId'] for x in trainer.get_examples() ]:
    trainer.delete_example(e_id)
  # delete intent
  for i in trainer.get_intents():
    if i['name'] != 'None':
      trainer.delete_intent(i['id'])
  # delete entities
  for e_id in [ x['id'] for x in trainer.get_entities() ]:
    trainer.delete_entity(e_id)

  trainer.update()

#------------------------------------------------------------------------------
main()
