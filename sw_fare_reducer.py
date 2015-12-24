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
		SMTP_PASSWORD = ""
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
## Set directory path and file name for logs
#####################################################################
cwd = os.getcwd()
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_fare_reducer.log"

def main():
	flightSearchArray = []
	farePriceAlert = False
	#####################################################################
	## Retrieve list of upcoming reserved flights
	#####################################################################
	db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
	cursor = db.cursor()

	sql = "SELECT DISTINCT GROUP_CONCAT(UPCOMING_FLIGHTS.DEPART_AIRPORT_CODE ORDER BY UPCOMING_FLIGHTS.DEPART_DATE_TIME ASC), \
			GROUP_CONCAT(UPCOMING_FLIGHTS.ARRIVE_AIRPORT_CODE ORDER BY UPCOMING_FLIGHTS.DEPART_DATE_TIME ASC), \
			GROUP_CONCAT(DATE_FORMAT(UPCOMING_FLIGHTS.DEPART_DATE_TIME, '%Y-%m-%d') ORDER BY UPCOMING_FLIGHTS.DEPART_DATE_TIME ASC) \
			FROM UPCOMING_FLIGHTS \
			RIGHT JOIN RESERVED_FLIGHTS \
			ON UPCOMING_FLIGHTS.UPCOMING_FLIGHT_ID=RESERVED_FLIGHTS.UPCOMING_FLIGHT_ID \
			GROUP BY RESERVED_FLIGHTS.CONFIRMATION_NUM \
			ORDER BY UPCOMING_FLIGHTS.DEPART_DATE_TIME ASC,UPCOMING_FLIGHTS.DEPART_AIRPORT_CODE ASC,UPCOMING_FLIGHTS.ARRIVE_AIRPORT_CODE ASC"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		for row in results:
			if "," in row[0]:
				departAirportCode1 = row[0].split(',')[0]
				arriveAirportCode1 = row[0].split(',')[1]
			else:
				departAirportCode1 = row[0].split(',')[0]
				arriveAirportCode1 = False

			if  "," in row[1]:
				departAirportCode2 = row[1].split(',')[0]
				arriveAirportCode2 = row[1].split(',')[1]
			else:
				departAirportCode2 = row[1].split(',')[0]
				arriveAirportCode2 = False
			
			if  "," in row[2]:
				departDate = row[2].split(',')[0]
				returnDate = row[2].split(',')[1]
			else:
				departDate = row[2].split(',')[0]
				returnDate = False

			i = 0
			departFlag = False
			returnFlag = False
			# Roundtrip flight with same airports. i.e SJC->LAS and LAS->SJC
			if departAirportCode1 == arriveAirportCode2 and departAirportCode2 == arriveAirportCode1:
				if len(flightSearchArray) > 0:
					for i in range(0,len(flightSearchArray)):
						if departAirportCode1 == flightSearchArray[i][0] and arriveAirportCode1 == flightSearchArray[i][1] and departDate == flightSearchArray[i][2]:
							departFlag = True
						elif arriveAirportCode1 == flightSearchArray[i][0] and departAirportCode1 == flightSearchArray[i][1] and returnDate == flightSearchArray[i][2]:
							returnFlag = True
					if not departFlag:
						flightSearchArray.append([departAirportCode1,arriveAirportCode1,departDate,False])
					if not returnFlag:
						flightSearchArray.append([arriveAirportCode1,departAirportCode1,returnDate,False])
				else:
					flightSearchArray.append([departAirportCode1,arriveAirportCode1,departDate,False])
					flightSearchArray.append([arriveAirportCode1,departAirportCode1,returnDate,False])
			# Roundtrip flight with different airports. i.e SJC->LAS and LAS->OAK
			elif departAirportCode1 != arriveAirportCode2 and departAirportCode2 == arriveAirportCode1:
				if len(flightSearchArray) > 0:
					for i in range(0,len(flightSearchArray)):
						if departAirportCode1 == flightSearchArray[i][0] and arriveAirportCode1 == flightSearchArray[i][1] and departDate == flightSearchArray[i][2]:
							departFlag = True
						elif departAirportCode2 == flightSearchArray[i][0] and arriveAirportCode2 == flightSearchArray[i][1] and returnDate == flightSearchArray[i][2]:
							returnFlag = True
					if not departFlag:
						flightSearchArray.append([departAirportCode1,arriveAirportCode1,departDate,False])
					if not returnFlag:
						flightSearchArray.append([departAirportCode2,arriveAirportCode2,returnDate,False])
				else:
					flightSearchArray.append([departAirportCode1,arriveAirportCode1,departDate,False])
					flightSearchArray.append([departAirportCode2,arriveAirportCode2,returnDate,False])
			# One way flight. i.e. SJC->LAS
			elif not returnDate:
				if len(flightSearchArray) > 0:
					returnDate = ( datetime.datetime.strptime(departDate, "%Y-%m-%d") + datetime.timedelta(days=1) ).strftime("%Y-%m-%d")
					for i in range(0,len(flightSearchArray)):
						if departAirportCode1 == flightSearchArray[i][0] and departAirportCode2 == flightSearchArray[i][1] and departDate == flightSearchArray[i][2]:
							departFlag = True
					if not departFlag:
						flightSearchArray.append([departAirportCode1,departAirportCode2,departDate,False])
				else:
					flightSearchArray.append([departAirportCode1,departAirportCode2,departDate,False])

		flightSearchArray = sorted(flightSearchArray, key=lambda x: (x[2], x[0], x[1], x[3]), reverse=False)
		i = 0
		while i < len(flightSearchArray):
			if not flightSearchArray[i][3]:
				j = 0
				while j < len(flightSearchArray):
					if flightSearchArray[i][1] == flightSearchArray[j][0] and flightSearchArray[i][0] == flightSearchArray[j][1] and datetime.datetime.strptime(flightSearchArray[j][2], "%Y-%m-%d") > datetime.datetime.strptime(flightSearchArray[i][2], "%Y-%m-%d"):
						flightSearchArray[i][3] = flightSearchArray[j][2]
						flightSearchArray.pop(j)
						i = i - 1
						break
					elif j == len(flightSearchArray)-1:
						flightSearchArray[i][3] = ( datetime.datetime.strptime(flightSearchArray[i][2], "%Y-%m-%d") + datetime.timedelta(days=1) ).strftime("%Y-%m-%d")
					j = j + 1
			i = i + 1
	
		for x in flightSearchArray:
			departAirportCode = x[0]
			arriveAirportCode = x[1]
			departDate = x[2]
			returnDate = x[3]
			try:
				flightSearch = "python sw_flight_search.py %s %s %s %s" % (departAirportCode,arriveAirportCode,departDate,returnDate)
				os.system(flightSearch)
			except:
				logF = open(logFile, "a")
				logMessage = "%s ERROR: Unable to execute sw_flight_search.py [depart:%s|arrive:%s|date:%s|return:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,returnDate)
				logF.write(logMessage)
				logF.close()
	except:
		logF = open(logFile, "a")
		logMessage = "%s ERROR: Unable to select distinct reservations by confirmation number\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
		logF.write(logMessage)
		logF.close()
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
			else:
				farePriceAlert = False

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
		logMessage = "%s ERROR: Unable to select distinct reserved flights for price comparison\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
		logF.write(logMessage)
		logF.close()
		db.close()
		return 1

	return 0

main()