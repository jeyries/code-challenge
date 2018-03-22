#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)

CHIMP = """
    docker container run --interactive --rm --cpus="1" --memory="512m" --network=none \
        jeyries2/challenge python3 chimp.py
"""

PROMPT = "(Chimp) "
END_OF_FILE = "===end-of-file===4NGGI9ye2VJriT2Pdc9YrzCPVQSxNFnBcYtDsrayYV0HsMBG==="

class ChimpTool(object):

    def __init__(self):
        self.proc = subprocess.Popen( CHIMP, shell=True,
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=None, 
            bufsize=1,
            universal_newlines=True)

    def write(self, txt):
        logger.debug('write %s', txt.rstrip())
        self.proc.stdin.write(txt)

    def writeline(self, txt):
        logger.debug('writeline %s', txt)
        self.proc.stdin.write(txt)
        self.proc.stdin.write("\n")

    def readline(self):
        txt = self.proc.stdout.readline(1024)
        logger.debug('readline %s', txt.rstrip())
        return txt

    def prompt(self):
        found = self.proc.stdout.read(len(PROMPT))
        if len(found)==0:
            logger.error("unexpected end of file")
            raise ValueError("unexpected end of file")
        if found != PROMPT:
            logger.error("wrong prompt, found %s", found)
            raise ValueError("wrong prompt")

    def execute(self, command):
        logger.debug('execute %s', command)

        self.prompt()
        self.writeline(command)
        result = self.readline()
        if not result.startswith("success"):
            logger.debug("bad result: %s", result.rstrip())
            return False

        return True

    def quit(self):
        logger.debug('quit')

        self.prompt()
        self.writeline("quit")
        self.proc.wait()

    def upload(self, src, dst):
        logger.debug('upload %s %s', src, dst)

        self.prompt()
        self.writeline("upload %s" % dst)
  
        need_newline = False
        with open(src, "rt") as f:
            for line in f:
                need_newline = not line.endswith("\n")
                self.write(line)

        if need_newline:
            self.writeline("")
        self.writeline(END_OF_FILE)

    def download(self, src, dst):
        logger.debug('download %s %s', src, dst)

        self.prompt()
        self.writeline("download %s" % src)

        with open(dst, "wt") as f:
            while True:
                line = self.readline()
                if len(line)==0 or line.startswith(END_OF_FILE):
                    break
                f.write(line)


#################

def unlink(path):
    if os.path.exists(path):
        os.unlink(path)

def verify(language, samplecode):

    logger.info("verifying language %s", language)

    unlink("stdin.txt")
    unlink("stdout.txt")
    unlink("stderr.txt")

    with open("stdin.txt", "wt") as f:
        f.write("nothing here.")

    chimp = ChimpTool()
    chimp.upload(samplecode, "answer.txt")
    chimp.upload("stdin.txt", "stdin.txt")
    success = chimp.execute(language)
    chimp.download("stdout.txt", "stdout.txt")
    chimp.download("stderr.txt", "stderr.txt")
    if not success:
        raise ValueError("execution failed")

    
    chimp.quit()

    with open("stdout.txt", "rt") as f:
        stdout = f.read()

    logger.info("result: %s", stdout.rstrip())

    assert stdout.startswith("Hello")

def test():
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    verify("c", "../sample/sample.c")
    verify("cpp", "../sample/sample.cpp")
    verify("python", "../sample/sample.py")
    verify("javascript", "../sample/sample.js")
    verify("java", "../sample/sample.java")
    verify("swift", "../sample/sample.swift")
    verify("go", "../sample/sample.go")
    verify("scala", "../sample/sample.scala")
    verify("kotlin", "../sample/sample.kt")

#######

if __name__ == "__main__":
    test()
