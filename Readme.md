
# Prerequisites

Docker
Python 3, Pip

# step 1: clone server and content

mkdir ~/.challenge
cd ~/.challenge
git clone git@github.com:jeyries/code-challenge.git repo
git clone git@github.com:jeyries/code-challenge-content.git content

# step 2: install Python requirements

cd repo
pip3 install --requirement server/requirements.txt

# step 3: configuration

cp config.example.yml ~/.challenge/config.yml
edit the configuration file

# step 4: init database

export FLASK_APP=~/.challenge/repo/server/server.py
flask initdb

# step 5: build the container

docker build -t jeyries2/challenge container

# step 6: run worker

flask watch

# step 7: run web server

(in an other terminal)
flask run

# step 8: open in browser

open http://127.0.0.1:5000
