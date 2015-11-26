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

global errorFlag
global errorMessageFlag
global errorMessage

class MyHTMLParserErrors(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global errorFlag
		global errorMessageFlag
		if "div" in tag:
			for attr in attrs:
				if "class" in attr[0].lower() and "errors" in attr[1].lower():
					errorFlag = True
		if errorFlag and "p" in tag:
			errorMessageFlag = True
	def handle_endtag(self, tag):
		global errorFlag
		global errorMessageFlag
		if "p" in tag and errorFlag and errorMessageFlag:
			errorFlag = False
			errorMessageFlag = False
	def handle_data(self, data):
		global errorFlag
		global errorMessageFlag
		global errorMessage
		if errorFlag and errorMessageFlag:
			errorMessage = errorMessage+data

errorFlag = False
errorMessageFlag = False
errorMessage = ""

#####################################################################
## Set directory path and file name for response & results html file
#####################################################################
cwd = os.getcwd()
resultsFile = cwd+"/routemap_dyn.html"
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_route_map.log"

#####################################################################
## Initiate mechanize, set parameters in form, and submit form
#####################################################################
print "\nRetrieving flight routes...\n"
try:
	br = mechanize.Browser()
	br.set_handle_robots(False)
	results = br.open("https://www.southwest.com/flight/routemap_dyn.html")
	resultsContent = results.read()
except:
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Unable to retrieve flight routes\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
	logF.write(logMessage)
	logF.close()
	exit()

#####################################################################
## Search results string for errors
#####################################################################
parser = MyHTMLParserErrors()
parser.feed(resultsContent)
if errorMessage:
	endPos = errorMessage.rfind(".")
	errorMessage = errorMessage[:endPos+1]
	logF = open(logFile, "a")
	logMessage = "%s ERROR: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),errorMessage)
	print logMessage
	logF.write(logMessage)
	logF.close()
	exit()
else:
	with open(resultsFile, "w") as f:
	    f.write(resultsContent)