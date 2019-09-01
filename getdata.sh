#!/bin/bash

source ~/env/wx/bin/activate
source ~/src/wx/wx_env
cd /home/dane/src/wx
git pull
python get_reading.py
curl -L http://w4e.herokuapp.com/checkin/KHQSVXIG

