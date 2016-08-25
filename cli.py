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


def main(args=None):
  cli = argparse.ArgumentParser(
    description=__doc__,
    epilog='ex: python cli.py train settings.ini train_set.txt')
  cli.add_argument('command', metavar='COMMAND', help='{ train | test }',
                   choices=(TRAIN, TEST))
  cli.add_argument('config', metavar='CONFIG', help='config file with settings')
  cli.add_argument('dataset', metavar='DATASET', help='dataset file')

  options  = cli.parse_args(args=args)
  cp = ConfigParser.RawConfigParser()
  cp.read(options.config)
  settings = aadict(cp.items('nlu_trainer'))

  trainer = asset.symbol(settings.driver)(settings)
  if options.command == TRAIN:
    with open(options.dataset) as csv_file:
      r = csv.reader(csv_file)
      trainer.train_set(r)
  # elif options.command == TEST:
  #   trainer.test_set(options.dataset)

#------------------------------------------------------------------------------
main()
