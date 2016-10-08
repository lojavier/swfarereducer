#!/usr/bin/python
import os
import re
import sys
import json
import time
import urllib2
import MySQLdb
import smtplib
import datetime
import mechanize
import subprocess
from datetime import date
from HTMLParser import HTMLParser
from email.mime.text import MIMEText
from htmlentitydefs import name2codepoint
from sw_logger import LOG_INFO,LOG_ERROR,LOG_WARNING,LOG_DEBUG

#####################################################################
## Set directory path and global variables
#####################################################################
db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
checkinAlertMinutes = 30
utc_datetime = datetime.datetime.utcnow()
currentUtcDateTime = datetime.datetime.strptime(utc_datetime.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
checkinAlertDateTime = datetime.datetime.strptime(utc_datetime.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=24,minutes=checkinAlertMinutes)

#####################################################################
## Send checkin alert
#####################################################################
def sendCheckinAlert(notificationAddress,confirmationNum,departAirportCode,arriveAirportCode,departDateTime,flightNum):
	try:
		SMTP_SERVER = "smtp.gmail.com"
		SMTP_PORT = 587
		SMTP_USERNAME = "swfarereducer@gmail.com"
		p = subprocess.Popen('openssl rsautl -decrypt -inkey /home/pi/swfarereducer/keys/private_alert_key.pem -in /home/pi/swfarereducer/keys/encrypt_alert.dat'.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		SMTP_PASSWORD = p.stdout.readline().strip()
		EMAIL_FROM = 'swfarereducer@gmail.com'
		EMAIL_TO = [notificationAddress]
		EMAIL_SPACE = ", "
		EMAIL_SUBJECT = "FLIGHT CHECKIN ALERT!"
		DATA = "[CONF#%s] [%s->%s] [%s] [FLIGHT#%s] southwest.com/flight/retrieveCheckinDoc.html" % (confirmationNum,departAirportCode,arriveAirportCode,departDateTime,flightNum)
		msg = MIMEText(DATA)
		msg['Subject'] = EMAIL_SUBJECT
		msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
		msg['From'] = EMAIL_FROM
		mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
		mail.starttls()
		mail.login(SMTP_USERNAME, SMTP_PASSWORD)
		mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
		mail.quit()
		return 0
	except:
		return 1

def main():
	global db
	#####################################################################
	## Delete past flights 
	#####################################################################
	cursor = db.cursor()
	sql = "SELECT GROUP_CONCAT(RESERVED_FLIGHTS.RESERVED_FLIGHT_ID),GROUP_CONCAT(UPCOMING_FLIGHTS.UPCOMING_FLIGHT_ID) \
			FROM RESERVED_FLIGHTS \
			LEFT JOIN UPCOMING_FLIGHTS \
			ON UPCOMING_FLIGHTS.UPCOMING_FLIGHT_ID=RESERVED_FLIGHTS.UPCOMING_FLIGHT_ID \
			LEFT JOIN AIRPORTS \
			ON UPCOMING_FLIGHTS.DEPART_AIRPORT_CODE=AIRPORTS.AIRPORT_CODE \
			WHERE CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Aruba','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Atlantic Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/New_York','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Eastern Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Chicago','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Central Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Denver','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Mountain Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Phoenix','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Mountain Standard Time' AND AIRPORTS.AIRPORT_CITY LIKE '%%AZ%%' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/La_Paz','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Mexican Pacific Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Los_Angeles','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Pacific Standard Time' \
			ORDER BY UPCOMING_FLIGHTS.DEPART_DATE_TIME ASC" % (currentUtcDateTime,currentUtcDateTime,currentUtcDateTime,currentUtcDateTime,currentUtcDateTime,currentUtcDateTime,currentUtcDateTime)
	try:
		cursor.execute(sql)
		results = cursor.fetchone()
		if str(results[0]) != "None":
			reservedFlightIdArray = results[0].split(',')
			for reservedFlightId in reservedFlightIdArray:
				sql = "DELETE FROM RESERVED_FLIGHTS WHERE RESERVED_FLIGHTS.RESERVED_FLIGHT_ID='%s'" % (reservedFlightId)
				try:
					cursor.execute(sql)
					db.commit()
				except:
					db.rollback()
					LOG_ERROR(os.path.basename(__file__),"Failed to delete reserved flight [id:%s]" % (reservedFlightId))
		if str(results[1]) != "None":
			upcomingFlightIdArray = results[1].split(',')
			for upcomingFlightId in upcomingFlightIdArray:
				sql = "DELETE FROM UPCOMING_FLIGHTS WHERE UPCOMING_FLIGHTS.UPCOMING_FLIGHT_ID='%s'" % (upcomingFlightId)
				try:
					cursor.execute(sql)
					db.commit()
				except:
					db.rollback()
					LOG_ERROR(os.path.basename(__file__),"Failed to delete past flight [id:%s]" % (upcomingFlightId))
	except:
		LOG_ERROR(os.path.basename(__file__),"Failed to select past flights to delete")
		db.close()
		return 1

	#####################################################################
	## Retrieve list of upcoming reserved flights
	#####################################################################
	sql = "SELECT RESERVED_FLIGHTS.RESERVED_FLIGHT_ID,RESERVED_FLIGHTS.EMAIL,RESERVED_FLIGHTS.PHONE_NUM,WIRELESS_CARRIERS.CARRIER_TEXT_EMAIL,RESERVED_FLIGHTS.CONFIRMATION_NUM,UPCOMING_FLIGHTS.DEPART_AIRPORT_CODE,UPCOMING_FLIGHTS.ARRIVE_AIRPORT_CODE,UPCOMING_FLIGHTS.DEPART_DATE_TIME,UPCOMING_FLIGHTS.FLIGHT_NUM,AIRPORTS.AIRPORT_TIMEZONE \
			FROM RESERVED_FLIGHTS \
			LEFT JOIN UPCOMING_FLIGHTS \
			ON UPCOMING_FLIGHTS.UPCOMING_FLIGHT_ID=RESERVED_FLIGHTS.UPCOMING_FLIGHT_ID \
			LEFT JOIN WIRELESS_CARRIERS \
			ON RESERVED_FLIGHTS.WIRELESS_CARRIER_ID=WIRELESS_CARRIERS.WIRELESS_CARRIER_ID \
			LEFT JOIN AIRPORTS \
			ON UPCOMING_FLIGHTS.DEPART_AIRPORT_CODE=AIRPORTS.AIRPORT_CODE \
			WHERE CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Aruba','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Atlantic Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/New_York','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Eastern Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Chicago','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Central Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Denver','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Mountain Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Phoenix','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Mountain Standard Time' AND AIRPORTS.AIRPORT_CITY LIKE '%%{AZ}%%' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/La_Paz','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Mexican Pacific Standard Time' \
			OR CONVERT_TZ(UPCOMING_FLIGHTS.DEPART_DATE_TIME,'America/Los_Angeles','+00:00')<='%s' AND AIRPORTS.AIRPORT_TIMEZONE='Pacific Standard Time' \
			AND RESERVED_FLIGHTS.CHECKIN_ALERT=0 ORDER BY UPCOMING_FLIGHTS.DEPART_DATE_TIME ASC" % (checkinAlertDateTime,checkinAlertDateTime,checkinAlertDateTime,checkinAlertDateTime,checkinAlertDateTime,checkinAlertDateTime,checkinAlertDateTime)
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		for row in results:
			reservedFlightId = row[0]
			email = str(row[1])
			phoneNum = str(row[2])
			textEmail = str(row[3])
			confirmationNum = row[4]
			departAirportCode = row[5]
			arriveAirportCode = row[6]
			departDateTime = row[7].strftime('%a %b %d %I:%M%p')
			flightNum = row[8]
			timezone = row[9]
			if email == "None":
				notificationAddress = "%s%s" % (phoneNum,textEmail)
			else:
				notificationAddress = email
			LOG_DEBUG(os.path.basename(__file__),"%s %s %s %s %s %s" % (notificationAddress,confirmationNum,departAirportCode,arriveAirportCode,departDateTime,flightNum))
			if not sendCheckinAlert(notificationAddress,confirmationNum,departAirportCode,arriveAirportCode,departDateTime,flightNum):
				try:
					sql = "UPDATE RESERVED_FLIGHTS SET CHECKIN_ALERT='%s',CHECKIN_ALERT_TIMESTAMP='%s' WHERE RESERVED_FLIGHT_ID='%s'" % ('1',time.strftime("%Y-%m-%d %H:%M:%S"),reservedFlightId)
					cursor.execute(sql)
					db.commit()
				except:
					db.rollback()
					LOG_ERROR(os.path.basename(__file__),"Failed to update checkin alert flag [reservedFlightId:%s]" % (reservedFlightId))
			else:
				LOG_ERROR(os.path.basename(__file__),"Failed to send checkin alert [reservedFlightId:%s]" % (reservedFlightId))
	except:
		LOG_ERROR(os.path.basename(__file__),"Failed to select reserved flights for checkin")
		db.close()
		return 1

	db.close()
	LOG_INFO(os.path.basename(__file__),"Successfully finished checkin alerts")
	return 0

main()
