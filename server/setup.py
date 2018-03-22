#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import uuid

if not sys.version_info >= (3,4):
    print("check your python version.")
    exit(0)

from model import db, DATABASE
from model import User, Task, Record

print("remove database")
if os.path.exists(DATABASE):
	os.remove(DATABASE)

print("connect database")
db.connect()

print("create tables")
db.create_tables([User, Task, Record])


print("close database")
db.close()
