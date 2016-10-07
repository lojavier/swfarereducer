#!/bin/bash

SW_PATH=/home/pi/swfarereducer
APP_PATH=$SW_PATH/app
LOG_PATH=$SW_PATH/logs/sys.log
WEB_PATH=/var/www
KEY_PATH=$SW_PATH/keys

echo "$(date +'%Y-%m-%d %H:%M:%S') info update.sh: Starting update..." >> $LOG_PATH

cd $SW_PATH
git pull > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not retrieve update from GitHub" >> $LOG_PATH
	exit 1
fi

diff -r $APP_PATH $WEB_PATH > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') info update.sh: App update detected" >> $LOG_PATH

	passphrase=`openssl rsautl -decrypt -inkey $KEY_PATH/private_update_key.pem -in $KEY_PATH/encrypt_update.dat`
	if [ "$passphrase" = "" ]; then
		echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Failed to retrieve openssl passphrase" >> $LOG_PATH
	fi

	echo '$passphrase' | sudo -S rm -rf $WEB_PATH/*
	if [ $? -ne 0 ]; then
		echo "$(date +'%Y-%m-%d %H:%M:%S') warning update.sh: Could not remove all $WEB_PATH files" >> $LOG_PATH
	fi

	echo '$passphrase' | sudo -S cp -rf $APP_PATH/* $WEB_PATH/.
	if [ $? -ne 0 ]; then
		echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not copy $APP_PATH files into $WEB_PATH" >> $LOG_PATH
		exit 1
	fi
else
	echo "$(date +'%Y-%m-%d %H:%M:%S') info update.sh: No app update available" >> $LOG_PATH
fi

echo "$(date +'%Y-%m-%d %H:%M:%S') info update.sh: Update successful!" >> $LOG_PATH

sync
