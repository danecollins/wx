#!/bin/bash -l

source /Users/dane/dropbox/osx/env_vars/wx_vars

DATE=`date +%Y-%m-%d`
backup_file=/Users/dane/dropbox/dacxl/TrackPlaces/backups/wxdb.$DATE

echo "backing up $AWS_DB_DBNAME"
export PGPASSWORD=$AWS_DB_PASS

pg_dump --dbname=$AWS_DB_DBNAME --host=$AWS_DB_HOST --username=$AWS_DB_UNAME -F c -f $backup_file

