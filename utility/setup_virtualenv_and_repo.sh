#!/bin/bash
mkvirtualenv aac_dash --python=python3.6
pip install -r requirements.txt
git init
git add .
git commit -m "Initial commit"
