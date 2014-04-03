#!/bin/bash
# add a line to "/etc/crontab" like:
# 30 18   * * 7   root    sh /media/sf_GitHub/crike/src/crike_django/backupdb.sh

DATE=`date +"%Y-%m-%d"`
mongodump --db crikedb --out /opt/backup/mongodb-dump-$DATE
