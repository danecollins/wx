#!/bin/bash

source ~/env/wx/bin/activate
source ~/src/wx/wx_env
cd /home/dane/src/wx
echo "----------- git pull to make sure code is up to date --------"
git pull
echo "-------------------------------------------------------------"
python get_reading.py
curl -L http://w4e.herokuapp.com/checkin/KHQSVXIG

