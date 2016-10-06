#!/bin/bash

SW_PATH=/home/pi/swfarereducer
SCRIPTS_PATH=$SW_PATH/scripts
LOG_PATH=$SW_PATH/logs/sys.log

echo "$(date +'%Y-%m-%d %H:%M:%S') info update.sh: Starting update..." >> $LOG_PATH

sudo mv -f $SW_PATH/css /var/www/.
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not update CSS files" >> $LOG_PATH
fi

sudo mv -f $SW_PATH/*.php /var/www/.
if [ $? -ne 0 ]; then
	echo "$(date +'%Y-%m-%d %H:%M:%S') error update.sh: Could not update PHP files" >> $LOG_PATH
fi

sync
