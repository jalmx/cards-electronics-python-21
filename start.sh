#! /bin/bash

python3 -m venv .
source ./bin/activate
pip install notebook
jupyter notebook ./book