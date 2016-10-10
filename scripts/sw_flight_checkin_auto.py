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
## Set directory path and file name for response & results html file
## Set global variables
#####################################################################
p = subprocess.Popen('openssl rsautl -decrypt -inkey /home/pi/swfarereducer/keys/private_database_key.pem -in /home/pi/swfarereducer/keys/encrypt_database.dat'.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
db_pass = p.stdout.readline().strip()
db = MySQLdb.connect("127.0.0.1","root",db_pass,"SWFAREREDUCERDB")
cwd = os.path.dirname(os.path.realpath(__file__))
responseFile = cwd+"/../docs/sw_flight_checkin_auto_response.html"
resultsFile = cwd+"/../docs/sw_flight_checkin_auto_results.html"
checkinUrl = "https://www.southwest.com/flight/retrieveCheckinDoc.html?forceNewSession=yes"
# checkinUrl = "https://www.southwest.com/flight/retrieveCheckinDoc.html"
errorFlag=""
errorMessageFlag=""
errorMessage=""
confirmationNum=""
firstName=""
lastName=""

#####################################################################
## Parse HTML output
#####################################################################
class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		# global temp
		# global flightNum
		# global farePriceDollars
		# global departTag
		# global departTime
		# global arriveTag
		# global arriveTime
		# global flightRoute
		# global pointsFlag
		global errorFlag
		global errorMessageFlag
		# if "input" in tag:
			# for attr in attrs:
			# 	if "title" in attr[0]:
			# 		result = attr[1].split(' ', 8)
			# 		flightNum = result[2]
			# 		farePriceDollars = result[3].replace('$','')
			# 		temp = datetime.datetime.strptime(result[4], "%I:%M%p")
			# 		departTime = temp.strftime("%H:%M:%S")
			# 		departTag = result[5]
			# 		temp = datetime.datetime.strptime(result[6], "%I:%M%p")
			# 		arriveTime = temp.strftime("%H:%M:%S")
			# 		arriveTag = result[7]
			# 		flightRoute = result[8]
			# 		temp = flightRoute.lower()
		# elif "label" in tag:
			# for attr in attrs:
			# 	if "class" in attr[0] and "product_price" in attr[1]:
			# 		pointsFlag = True
		if "div" in tag:
			for attr in attrs:
				if "class" in attr[0].lower() and "oopserror" in attr[1].lower():
					errorFlag = True
		elif "li" in tag and errorFlag:
			errorMessageFlag = True
	def handle_endtag(self, tag):
		global errorFlag
		global errorMessageFlag
		if "li" in tag and errorFlag and errorMessageFlag:
			errorFlag = False
			errorMessageFlag = False
	def handle_data(self, data):
		# global farePricePoints
		# global pointsFlag
		global errorFlag
		global errorMessageFlag
		global errorMessage
		# if pointsFlag:
		# 	farePricePoints = data.replace(',','')
		# 	pointsFlag = False
		if errorFlag and errorMessageFlag:
			errorMessage = errorMessage+data

# class MyHTMLParserErrors(HTMLParser):
# 	def handle_starttag(self, tag, attrs):
# 		global errorFlag
# 		global errorMessageFlag
# 		if "div" in tag:
# 			for attr in attrs:
# 				if "class" in attr[0].lower() and "oopserror" in attr[1].lower():
# 					errorFlag = True
# 		if errorFlag and "li" in tag:
# 			errorMessageFlag = True
# 	def handle_endtag(self, tag):
# 		global errorFlag
# 		global errorMessageFlag
# 		if "li" in tag and errorFlag and errorMessageFlag:
# 			errorFlag = False
# 			errorMessageFlag = False
# 	def handle_data(self, data):
# 		global errorFlag
# 		global errorMessageFlag
# 		global errorMessage
# 		if errorFlag and errorMessageFlag:
# 			errorMessage = errorMessage+data

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

checkinAlertMinutes = 30
utc_datetime = datetime.datetime.utcnow()
currentUtcDateTime = datetime.datetime.strptime(utc_datetime.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
checkinAlertDateTime = datetime.datetime.strptime(utc_datetime.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=24,minutes=checkinAlertMinutes)

#####################################################################
## Search results string for errors
#####################################################################
def parseResults(resultsContent):
	global errorMessage
	parser = MyHTMLParser()
	parser.feed(resultsContent)
	if errorMessage:
		endPos = errorMessage.rfind(".")
		errorMessage = errorMessage[:endPos+1]
		LOG_ERROR(os.path.basename(__file__),errorMessage)
		errorMessage = ""
		return 1
	else:
		return 0

#####################################################################
## Get URL response and results
#####################################################################
def checkinViaSW():
	global responseFile
	global resultsFile
	global checkinUrl
	global confirmationNum
	global firstName
	global lastName
	try:
		br = mechanize.Browser()
		br.set_handle_robots(False)
		br.set_handle_refresh(False)
		response = br.open(checkinUrl)
		responseContent = response.read()
		# with open(responseFile, "w") as f:
		#     f.write(responseContent)
		formcount=0
		for form in br.forms():
			if str(form.attrs.get('id')) == "itineraryLookup":
				break
			formcount=formcount+1
		br.select_form(nr=formcount)
		# br.find_control(id="pnrFriendlyLookup_option_confirmationNumber",name="searchType").value = ['ConfirmationNumber']
		br.find_control(name="confirmationNumber").value = confirmationNum
		br.find_control(name="firstName").value = firstName
		br.find_control(name="lastName").value = lastName
		results = br.submit()
		resultsContent = results.read()
		# with open(resultsFile, "w") as f:
		# 	f.write(resultsContent)
		if parseResults(resultsContent) == 1:
			LOG_ERROR(os.path.basename(__file__),"Failed to checkin [firstName:%s|lastName:%s|confirmationNum:%s]" % (firstName,lastName,confirmationNum))
			return 1
		else:
			return 0
	except:
		LOG_ERROR(os.path.basename(__file__),"Failed to checkin via %s [firstName:%s|lastName:%s|confirmationNum:%s]" % (checkinUrl,firstName,lastName,confirmationNum))
		return 1

checkinViaSW()
								

def main():
	global db
	i = 0
	while i < 1:
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
				# if checkinViaSW() == 0:
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
		i = i + 1
	return 0

# main()
