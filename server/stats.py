#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from model import db
from model import User, Task

#################

db.connect()

users = User.select()

print("found %d users:" % len(users))
for user in users:
    print(user)

tasks = Task.select()

print("found %d tasks:" % len(tasks))
for task in tasks:
    print(task)


db.close()

