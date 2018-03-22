#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import yaml
import logging
import shutil
import datetime
import importlib.util

if not sys.version_info >= (3,4):
    print("check your python version.")
    exit(0)
    
from model import ROOT, db, isoformat
from model import User, Task, Challenge, Record

import chimptools
import validate

logger = logging.getLogger(__name__)

### config

with open(os.path.join(ROOT, 'config.yml'), "rt") as f:
    CONFIG = yaml.load(f)

CHALLENGES = [Challenge(info) for info in CONFIG['challenges']]

#################


LANGUAGES = [
  'python',
  'javascript',
  'java',
  'c',
  'cpp',
  'swift',
  'go',
  'scala',
]

class Tasker(object):

    def __init__(self, task):
        self.task = task
        self.challenge = next(x for x in CHALLENGES if x.identifier == self.task.challenge)
        self.now = 1
        self.chimp = chimptools.ChimpTool()

        self.validate = validate.validate
        path = os.path.join(self.challenge.folder, "validate.py")
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location('validate', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.validate = module.validate

    def next( self ):
        self.now += 1

    @property
    def done( self ):
        return self.now > self.challenge.max

    @property
    def input( self ):
        return os.path.join(self.challenge.folder, "input%d.txt" % self.now)

    @property
    def output( self ):
        return os.path.join(self.challenge.folder, "output%d.txt" % self.now)

    def info(self, txt):
        logger.info(txt)
        self.result.write(txt)
        self.result.write("\n")

    def check(self):
        self.info("checking step %d / %d ..." % (self.now, self.challenge.max) )

        self.task.now = self.now
        self.task.save()

        with open(self.task.meta, "rt") as f:
            meta = json.load(f)

        logger.debug("%r", meta)
        language = meta['language']
        assert language in LANGUAGES

        shutil.copyfile( self.input, self.task.stdin )
        self.chimp.upload(self.task.stdin, "stdin.txt")

        success = self.chimp.execute(language)

        self.chimp.download("stdout.txt", self.task.stdout)
        self.chimp.download("stderr.txt", self.task.stderr)

        if not success:
            self.info("failure !")
            with open(self.task.stdout, "rt") as f:
                for line in f:
                    self.result.write(line)
            with open(self.task.stderr, "rt") as f:
                for line in f:
                    self.result.write(line)
            return False
        
        score = self.validate(self.task.stdout, self.input, self.output, self.info)
        success = score > 0
        
        if success:
            self.info("success !")
        else:
            self.info("failure !")

        self.result.flush()
        return success

    def process(self):
        self.result = open(self.task.result, "wt")

        logger.info("process: %r", self.task)
        logger.debug("progress ...")

        self.task.state = "progress"
        self.task.save()

        #self.chimp.execute("cleanup")
        self.chimp.upload(self.task.answer, "answer.txt")

        success = True
        while not self.done:
            #time.sleep(3)
            result = self.check()
            self.next()
            if not result:
                success = False
                break

        self.chimp.quit()
        logger.debug("done.")

        self.result.close()

        if success:
            self.task.state = "done"
            self.task.save()

            user = self.task.user
            challenge = self.task.challenge
            records = user.records.where(Record.challenge == challenge).limit(1)
            record = records[0]
            record.solve()

        else:
            self.task.state = "failure"
            self.task.save()
        


#################

def watch():
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    chimptools.logger.setLevel(logging.DEBUG)
    chimptools.logger.addHandler(ch)

    db.connect()

    while True:
        tasks = Task.select().where(Task.state == 'todo').limit(1)

        if len(tasks) == 0:
            logger.info("nothing to do")
            time.sleep(1)
        else:
            Tasker(tasks[0]).process()

    db.close()


#################

def test1():
    tasks = Task.select().where(Task.state == 'todo').limit(1)
    task = tasks[0]
    print("task", task)

    #task.state = "done"
    #task.save()

    user = task.user
    print("user", user)

    challenge = task.challenge
    print("challenge", challenge)

    records = user.records.where(Record.challenge == challenge).limit(1)
    record = records[0]
    print("record", record)

    record.state = "done"
    record.solved_date = datetime.datetime.now()
    record.save()

    print("type", type(record))
    print("type", type(record.solved_date))
    print("isoformat", isoformat(record.solved_date))
    print("json", record.json)


def test2():

    spec = importlib.util.spec_from_file_location('validate', 'validate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    score = module.validate('output2.txt', 'input1.txt', 'output1.txt', print )
    print("score", score)

#######

if __name__ == "__main__":
    test2()