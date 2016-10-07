#!/usr/bin/python
import os
import sys
import time
import MySQLdb
import datetime
import subprocess
from sw_logger import LOG_INFO,LOG_ERROR,LOG_WARNING,LOG_DEBUG

#####################################################################
# MySQL database details to which backup to be done. Make sure below user having enough privileges to take databases backup. 
# To take multiple databases backup, create any file like /backup/dbnames.txt and put databses names one on each line and assignd to DB_NAME variable.
#####################################################################
DATETIME = time.strftime('%Y_%m_%d_%H_%M_%S')
cwd = os.path.dirname(os.path.realpath(__file__))

DB_HOST = 'localhost'
DB_USER = 'root'
p = subprocess.Popen('openssl rsautl -decrypt -inkey /home/pi/swfarereducer/keys/private_database_key.pem -in /home/pi/swfarereducer/keys/encrypt_database.dat'.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
DB_USER_PASSWORD = p.stdout.readline().strip()
DB_NAME = 'SWFAREREDUCERDB'
BACKUP_DIR = cwd+"/../sql/backup"
FILE_NAME = DB_NAME.lower() + "_" + DATETIME + ".sql"
BACKUP_PATH = BACKUP_DIR + "/" + FILE_NAME

#####################################################################
# Checking if backup folder already exists or not. If not exists will create it.
#####################################################################
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

#####################################################################
# Code for checking if you want to take single database backup or assinged multiple backups in DB_NAME.
#####################################################################
if os.path.exists(DB_NAME):
    file1 = open(DB_NAME)
    multi = True
else:
    multi = False

#####################################################################
# Starting actual database backup process.
#####################################################################
try:
    if multi:
        in_file = open(DB_NAME,"r")
        flength = len(in_file.readlines())
        in_file.close()
        p = 1
        dbfile = open(DB_NAME,"r")

        while p <= flength:
            db = dbfile.readline()   # reading database name from file
            db = db[:-1]         # deletes extra line
            dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + BACKUP_PATH
            os.system(dumpcmd)
            p = p + 1
        dbfile.close()
        LOG_INFO(os.path.basename(__file__),"Successfully backed up database!")
    else:
        db = DB_NAME
        dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + BACKUP_PATH
        os.system(dumpcmd)

    #####################################################################
    # Remove old database files older than 60 days
    #####################################################################
    try:
        expirationDays = 60
        now = str(datetime.datetime.now())
        pattern = '%Y-%m-%d %H:%M:%S.%f'
        currentTime = int(time.mktime(time.strptime(now, pattern)))
        listdir = os.listdir(BACKUP_DIR)
        for file in listdir:
            filePath = BACKUP_DIR+"/"+file
            fileTime = int(os.path.getmtime(filePath))
            fileAge = currentTime - fileTime
            if fileAge > (60*60*24*expirationDays):
                os.remove(filePath)
    except:
        LOG_ERROR(os.path.basename(__file__),"Failed to remove backup database files older than %d days" % (expirationDays))
except:
    LOG_ERROR(os.path.basename(__file__),"Failed to backup database")
