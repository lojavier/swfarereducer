#!/bin/bash

SW_PATH=/home/pi/swfarereducer
UPDATE_PATH=$SW_PATH/update
LOG_PATH=$SW_PATH/logs/sys.log
WEB_PATH=/var/www

echo "$(date +'%Y-%m-%d %H:%M:%S') info update.sh: Starting update..." >> $LOG_PATH

cd $SW_PATH
git checkout .
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not checkout files from git" >> $LOG_PATH
	exit 1
fi

sudo mkdir -p $UPDATE_PATH
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not create $UPDATE_PATH" >> $LOG_PATH
	exit 1
fi

sudo mv -f $SW_PATH/css $UPDATE_PATH/.
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not update CSS files" >> $LOG_PATH
	exit 1
fi

sudo mv -rf $SW_PATH/css /var/www/css
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not update CSS files" >> $LOG_PATH
	exit 1
fi

sudo mv -f $SW_PATH/*.php /var/www/.
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not update PHP files" >> $LOG_PATH
	exit 1
fi

sudo rm -rf /var/www/.
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not remove all $WEB_PATH files" >> $LOG_PATH
	exit 1
fi

sudo mv -f $SW_PATH/update/* $WEB_PATH/.
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not update website files" >> $LOG_PATH
	exit 1
fi

sudo rm -rf $UPDATE_PATH
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not create $UPDATE_PATH" >> $LOG_PATH
	exit 1
fi

sync
