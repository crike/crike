#!/bin/bash
# add a line to "/etc/crontab" like:
# 30 18   * * 7   root    sh /root/git/crike/src/crike_django/backupdb.sh

# for restore:
# mongorestore [--drop] /root/crike/data/backup/mongodb-dump-$DATE/crikedb

DATE=`date +"%Y-%m-%d"`
mongodump --db crikedb --out /root/crike/data/backup/mongodb-dump-$DATE
