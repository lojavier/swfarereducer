#!/usr/bin/env python
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
from datetime import date
from HTMLParser import HTMLParser
from email.mime.text import MIMEText
from htmlentitydefs import name2codepoint

#####################################################################
## Send price drop alert
#####################################################################
def sendPriceAlert(notificationAddress,confirmationNum,departAirportCode,arriveAirportCode,departDateTime,flightNum,farePricePaid,farePrice,fareLabel):
	try:
		SMTP_SERVER = "smtp.gmail.com"
		SMTP_PORT = 587
		SMTP_USERNAME = "swfarereducer@gmail.com"
		SMTP_PASSWORD = "calilife4me"
		EMAIL_FROM = 'swfarereducer@gmail.com'
		EMAIL_TO = [notificationAddress]
		EMAIL_SPACE = ", "
		EMAIL_SUBJECT = "FARE PRICE ALERT!"
		if fareLabel == "DOLLARS":
			DATA = "[$%s -> $%s] [CONF#%s] [%s->%s] [%s] [FLIGHT#%s] southwest.com/flight/change-air-reservation.html" % (farePricePaid,farePrice,confirmationNum,departAirportCode,arriveAirportCode,departDateTime,flightNum)
		elif fareLabel == "POINTS":
			DATA = "[%s -> %s] [CONF#%s] [%s->%s] [%s] [FLIGHT#%s] southwest.com/flight/change-air-reservation.html" % (farePricePaid,farePrice,confirmationNum,departAirportCode,arriveAirportCode,departDateTime,flightNum)
	
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

#####################################################################
## Set directory path and file name for response & results html file
#####################################################################
cwd = os.getcwd()
# responseFile = cwd+"/logs/lookup-air-reservation.html"
# resultsFile = cwd+"/logs/view-air-reservation.html"
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_fare_reducer.log"

def main():
	farePriceAlert = False
	#####################################################################
	## Retrieve list of upcoming reserved flights
	#####################################################################
	db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
	cursor = db.cursor()
	sql = "SELECT DISTINCT UPCOMING_FLIGHTS.DEPART_AIRPORT_CODE,UPCOMING_FLIGHTS.ARRIVE_AIRPORT_CODE,DATE_FORMAT(UPCOMING_FLIGHTS.DEPART_DATE_TIME, '%Y-%m-%d') \
			FROM UPCOMING_FLIGHTS \
			RIGHT JOIN RESERVED_FLIGHTS \
			ON UPCOMING_FLIGHTS.UPCOMING_FLIGHT_ID=RESERVED_FLIGHTS.UPCOMING_FLIGHT_ID"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		for row in results:
			departAirportCode = row[0]
			arriveAirportCode = row[1]
			departDate = row[2]
			returnDate = ( datetime.datetime.strptime(departDate, "%Y-%m-%d") + datetime.timedelta(days=1) ).strftime("%Y-%m-%d")
			flightSearch = "python sw_flight_search.py %s %s %s %s" % (departAirportCode,arriveAirportCode,departDate,returnDate)
			os.system(flightSearch)
	except:
		logF = open(logFile, "a")
		logMessage = "%s ERROR: Unable to select distinct flights\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
		logF.write(logMessage)
		logF.close()
		db.close()
		return 1

	sql = "SELECT RESERVED_FLIGHTS.RESERVED_FLIGHT_ID,RESERVED_FLIGHTS.EMAIL,RESERVED_FLIGHTS.PHONE_NUM,WIRELESS_CARRIERS.CARRIER_TEXT_EMAIL,RESERVED_FLIGHTS.CONFIRMATION_NUM,RESERVED_FLIGHTS.FARE_LABEL,RESERVED_FLIGHTS.FARE_PRICE_PAID,UPCOMING_FLIGHTS.DEPART_AIRPORT_CODE,UPCOMING_FLIGHTS.ARRIVE_AIRPORT_CODE,UPCOMING_FLIGHTS.DEPART_DATE_TIME,UPCOMING_FLIGHTS.FLIGHT_NUM,UPCOMING_FLIGHTS.FARE_PRICE_DOLLARS,UPCOMING_FLIGHTS.FARE_PRICE_POINTS \
			FROM UPCOMING_FLIGHTS \
			RIGHT JOIN RESERVED_FLIGHTS \
			ON UPCOMING_FLIGHTS.UPCOMING_FLIGHT_ID=RESERVED_FLIGHTS.UPCOMING_FLIGHT_ID \
			LEFT JOIN WIRELESS_CARRIERS \
			ON RESERVED_FLIGHTS.WIRELESS_CARRIER_ID=WIRELESS_CARRIERS.WIRELESS_CARRIER_ID"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		for row in results:
			reservedFlightId = row[0]
			email = str(row[1])
			phoneNum = str(row[2])
			textEmail = str(row[3])
			confirmationNum = row[4]
			fareLabel = row[5]
			farePricePaid = row[6]
			departAirportCode = row[7]
			arriveAirportCode = row[8]
			departDateTime = row[9].strftime('%a %b %d %I:%M%p')
			flightNum = row[10]
			farePriceDollars = row[11]
			farePricePoints = row[12]
			if email == "None":
				notificationAddress = "%s%s" % (phoneNum,textEmail)
			else:
				notificationAddress = email

			if fareLabel == "POINTS" and farePricePaid > farePricePoints:
				farePrice = farePricePoints
				farePriceAlert = True
			elif fareLabel == "DOLLARS" and farePricePaid > farePriceDollars:
				farePrice = farePriceDollars
				farePriceAlert = True

			if farePriceAlert:
				if not sendPriceAlert(notificationAddress,confirmationNum,departAirportCode,arriveAirportCode,departDateTime,flightNum,farePricePaid,farePrice,fareLabel):
					try:
						sql = "UPDATE RESERVED_FLIGHTS SET FARE_PRICE_ALERT='%s',FARE_PRICE_ALERT_TIMESTAMP='%s' WHERE RESERVED_FLIGHT_ID='%s'" % ('1',time.strftime("%Y-%m-%d %H:%M:%S"),reservedFlightId)
						cursor.execute(sql)
						db.commit()
					except:
						db.rollback()
						logF = open(logFile, "a")
						logMessage = "%s ERROR: Unable to update price alert flag [reservedFlightId:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),reservedFlightId)
						logF.write(logMessage)
						logF.close()
				else:
					logF = open(logFile, "a")
					logMessage = "%s ERROR: Unable to send price alert [reservedFlightId:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),reservedFlightId)
					logF.write(logMessage)
					logF.close()
	except:
		logF = open(logFile, "a")
		logMessage = "%s ERROR: Unable to select distinct flights\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
		logF.write(logMessage)
		logF.close()
		db.close()
		return 1

	return 0

main()