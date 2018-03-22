#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this will get executed in the container

import os
import os.path
import sys
import json
import shutil
import subprocess
from functools import wraps
from cmd import Cmd

PROMPT = "(Chimp) "
END_OF_FILE = "===end-of-file===4NGGI9ye2VJriT2Pdc9YrzCPVQSxNFnBcYtDsrayYV0HsMBG==="

def with_success(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            f(*args, **kwargs)
            sys.stdout.write("success\n")
        except:
            sys.stdout.write("failure\n")
    return decorated


class Chimp(Cmd):

    def __init__(self):
        super().__init__()
        self.prompt = PROMPT

    def do_quit(self, arg):
        return True

    def do_upload(self, arg):
        args = arg.split()
        dest = args[0]
        with open(dest, "wt") as f:
            while True:
                line = sys.stdin.readline()
                if len(line)==0 or line.startswith(END_OF_FILE):
                    break
                f.write(line)
        
    def do_download(self, arg):
        args = arg.split()
        source = args[0]
        need_newline = False
        if os.path.exists(source):
            with open(source, "rt") as f:
                while True:
                    line = f.readline()
                    if len(line)==0:
                        break
                    need_newline = not line.endswith("\n")
                    sys.stdout.write(line)
        
        # finally ..
        if need_newline:
            sys.stdout.write("\n")
        sys.stdout.write(END_OF_FILE)
        sys.stdout.write("\n")

    def do_cleanup(self, arg):
        for name in os.listdir("."):
            if name.startswith("."):
                continue
            if os.path.isfile(name):
                os.remove(name)

    def build(self, cmds):
        with open("stderr.txt", "wb") as stderr:
            subprocess.check_call(cmds, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=stderr, shell=False)


    def answer(self, cmds):
        with open("stdin.txt", "rb") as stdin:
            with open("stdout.txt", "wb") as stdout:
                with open("stderr.txt", "ab") as stderr:
                    subprocess.check_call(cmds, stdin=stdin, stdout=stdout, stderr=stderr, shell=False, timeout=10)

    @with_success
    def do_python(self, arg):
        if not os.path.exists("answer.py"):
            shutil.copyfile("answer.txt", "answer.py")

        self.answer(["python3", "answer.py"])

    @with_success
    def do_javascript(self, arg):
        if not os.path.exists("answer.js"):
            shutil.copyfile("answer.txt", "answer.js")

        self.answer(["nodejs", "answer.js"])

    @with_success
    def do_java(self, arg):
        if not os.path.exists("Answer.class"):
            shutil.copyfile("answer.txt", "answer.java")
            self.build(["javac", "answer.java"])

        self.answer(["java", "-classpath", ".", "Answer"])

    @with_success
    def do_c(self, arg):
        if not os.path.exists("answer"):
            shutil.copyfile("answer.txt", "answer.c")
            self.build(["gcc", "-o", "answer", "answer.c"])

        self.answer(["./answer"])

    @with_success
    def do_cpp(self, arg):
        if not os.path.exists("answer"):
            shutil.copyfile("answer.txt", "answer.cpp")
            self.build(["g++", "-o", "answer", "answer.cpp"])

        self.answer(["./answer"])

    @with_success
    def do_swift(self, arg):
        if not os.path.exists("answer"):
            shutil.copyfile("answer.txt", "answer.swift")
            self.build(["swiftc", "-o", "answer", "answer.swift"])

        self.answer(["./answer"])

    @with_success
    def do_go(self, arg):
        if not os.path.exists("answer.go"):
            shutil.copyfile("answer.txt", "answer.go")

        self.answer(["/opt/go/bin/go", "run", "answer.go"])

    @with_success
    def do_scala(self, arg):
        if not os.path.exists("Answer.class"):
            shutil.copyfile("answer.txt", "answer.scala")
            self.build(["scalac", "answer.scala"])

        self.answer(["scala", "Answer"])

    @with_success
    def do_kotlin(self, arg):
        if not os.path.exists("AnswerKt.class"):
            shutil.copyfile("answer.txt", "answer.kt")
            self.build(["kotlinc", "answer.kt"])

        self.answer(["kotlin", "AnswerKt"])



#####

if __name__ == '__main__':
    Chimp().cmdloop()

