===========
nlu_trainer
===========

nlu_trainer provides an easy way to train and test Natural Language Understanding (NLU) systems. It currently only support Microsoft Language Understanding Intelligent Service (LUIS) API, but the library is architected to enable other drivers.


Training
========

Start by creating a training set where each line contains text, its intent, and named entities (in yaml format).

.. code:: text

  What is a loggerhead turtle?,define,{ animal: loggerhead turtle }
  What are bengal tigers?,define,{ animal: bengal tigers }


Then run:

.. code:: shell

  python cli.py train settings.ini train_set.txt


Testing
=======

Create a testing set using the same format as the training set, then run:

.. code:: shell

  python cli.py test settings.ini test_set.txt
