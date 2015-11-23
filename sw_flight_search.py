#!/usr/bin/env python
import re
import sys
import time
import urllib
import urllib2
import smtplib
import datetime
import mechanize
from datetime import date
from HTMLParser import HTMLParser
from email.mime.text import MIMEText
from htmlentitydefs import name2codepoint
# http://www.blog.pythonlibrary.org/2012/06/08/python-101-how-to-submit-a-web-form/
# http://www.thetaranights.com/fill-online-form-using-python/
# http://wwwsearch.sourceforge.net/mechanize/download.html
global temp
global nonstopFlag
global pointsFlag
global outboundTime
global returnTime
global flightNum
global currentPrice
global departTag
global departTime
global departTime24Hour
global arriveTag
global arriveTime
global arriveTime24Hour
global route
global upcoming_trips

# def send_mail():
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "swfarereducer@gmail.com"
# SMTP_PASSWORD = "swfarereducer1"
# EMAIL_FROM = 'swfarereducer@gmail.com'
# EMAIL_TO = ['loj90@sbcglobal.net']
# EMAIL_SUBJECT = "Demo Email : "
# DATE_FORMAT = "%d/%m/%Y"
# EMAIL_SPACE = ", "
# DATA='This is the content of the email.'
# try:
# 	msg = MIMEText(DATA)
# 	msg['Subject'] = EMAIL_SUBJECT + " %s" % (date.today().strftime(DATE_FORMAT))
# 	msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
# 	msg['From'] = EMAIL_FROM
# 	mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
# 	mail.starttls()
# 	mail.login(SMTP_USERNAME, SMTP_PASSWORD)
# 	mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
# 	mail.quit()
# 	# smtpObj = smtplib.SMTP('localhost')
# 	# smtpObj.sendmail(sender, receivers, message)         
# 	print "Successfully sent email"
# except smtplib.SMTPException:
# 	print "Error: unable to send email"

class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global temp
		global flightNum
		global currentPrice
		global departTag
		global departTime
		global departTime24Hour
		global arriveTag
		global arriveTime
		global arriveTime24Hour
		global route
		for attr in attrs:
			if "title" in attr[0]:
				result = attr[1].split(' ', 8)
				flightNum = result[2]
				currentPrice = result[3]
				departTime = result[4]
				temp = time.strptime(departTime, "%I:%M%p")
				departTime24Hour = float(temp.tm_hour) + float(float(temp.tm_min) / 60)
				departTag = result[5]
				arriveTime = result[6]
				temp = time.strptime(arriveTime, "%I:%M%p")
				arriveTime24Hour = float(temp.tm_hour) + float(float(temp.tm_min) / 60)
				arriveTag = result[7]
				route = result[8]
				temp = route.lower()
	def handle_data(self, data):
		global currentPrice
		currentPrice = data.replace(',','')

upcoming_trips = []
upcoming_trips.append(['8ABYGC','Lorenzo','Javier','loj90@sbcglobal.net','SJC','PHX','10/02/2015','8:05PM','9:50PM','179','80.00','4291'])
upcoming_trips.append(['8ABYGC','Lorenzo','Javier','loj90@sbcglobal.net','PHX','SJC','10/06/2015','5:40AM','7:35AM','2787','60.00','2989'])
upcoming_trips.append(['HHGRHL','Lorenzo','Javier','loj90@sbcglobal.net','SJC','ONT','10/30/2015','8:20PM','9:30PM','2953','119.00','6798'])
upcoming_trips.append(['HN9RRZ','Lorenzo','Javier','loj90@sbcglobal.net','LAX','SJC','11/02/2015','8:45AM','9:55AM','1147','63.00','3184'])
upcoming_trips.append(['832STR','Lorenzo','Javier','loj90@sbcglobal.net','SJC','PHX','11/04/2015','6:35AM','9:20AM','539','60.00','2989'])
upcoming_trips.append(['832STR','Lorenzo','Javier','loj90@sbcglobal.net','PHX','SJC','11/08/2015','8:40PM','9:35PM','1117','144.00','8459'])

airport_list = []
airport_list.append(['OAK','Oakland, CA - OAK'])
airport_list.append(['SJC','San Jose, CA - SJC'])
airport_list.append(['SFO','San Francisco, CA - SFO'])
airport_list.append(['ONT','Ontario/LA, CA - ONT'])
airport_list.append(['SNA','Orange County/Santa Ana, CA - SN'])
airport_list.append(['LAX','Los Angeles, CA - LAX'])
airport_list.append(['LAS','Las Vegas, NV - LAS'])
airport_list.append(['PHX','Phoenix, AZ - PHX'])
airport_list.append(['SAN','San Diego, CA - SAN'])
airport_list.append(['ALB','Albany, NY - ALB'])
airport_list.append(['BUF','Buffalo/Niagara, NY - BUF'])
airport_list.append(['ISP','Long Island/Islip, NY - ISP'])
airport_list.append(['LGA','New York (LaGuardia), NY - LGA'])
airport_list.append(['EWR','New York/Newark, NJ - EWR'])
airport_list.append(['ROC','Rochester, NY - ROC'])
airport_list.append(['SMF','Sacramento, CA - SMF'])
airport_list.append(['SEA','Seattle/Tacoma, WA - SEA'])

#####################################################################
## Set user input variables
#####################################################################
temp = ""
originAirportCode = sys.argv[1]
originAirportName = False
for x in range(0,len(airport_list)):
	if originAirportCode in airport_list[x][0]:
		originAirportName = airport_list[x][1]
		break;
destinationAirportCode = sys.argv[2]
destinationAirportName = False
for x in range(0,len(airport_list)):
	if destinationAirportCode in airport_list[x][0]:
		destinationAirportName = airport_list[x][1]
		break;
outboundDate = sys.argv[3]
temp = datetime.datetime.strptime(outboundDate, "%m/%d/%Y")
outboundDay = temp.strftime("%A")
outboundTime = sys.argv[4]
if( ("<" in outboundTime) or (">" in outboundTime) ):
	if( "<" in outboundTime ):
		print outboundTime
	elif( ">" in outboundTime ):
		print outboundTime
returnDate = sys.argv[5]
temp = datetime.datetime.strptime(returnDate, "%m/%d/%Y")
returnDay = temp.strftime("%A")
returnTime = sys.argv[6]
nonstopFlag = False
if( str(sys.argv[7]).lower() == "nonstop" ):
	nonstopFlag = True
pointsFlag = False
if( str(sys.argv[8]).lower() == "points" ):
	pointsFlag = True

if(nonstopFlag and pointsFlag):
	print "\nSearching for all NONSTOP flights (POINTS)...\n"
elif(nonstopFlag and not pointsFlag):
	print "\nSearching for all NONSTOP flights (DOLLARS)...\n"
elif(not nonstopFlag and pointsFlag):
	print "\nSearching for all flights (POINTS)...\n"
elif(not nonstopFlag and not pointsFlag):
	print "\nSearching for all flights (DOLLARS)...\n"

currentPrice = "$0"
departTag = "depart"
departTime = "12:00AM"
arriveTag = "arrive"
arriveTime = "12:00AM"
route = "all"
flightNum = "0"

#####################################################################
## Initiate mechanize, set parameters in form, and submit form
#####################################################################
br = mechanize.Browser()
br.set_handle_robots(False)
response = br.open("https://www.southwest.com/flight/")
content = response.read()
with open("southwest_response.html", "w") as f:
    f.write(content)
br.select_form(name="buildItineraryForm")
# br.select_form(nr=2)
br.find_control(name="originAirport").value = [originAirportCode]
br.find_control(name="destinationAirport").value = [destinationAirportCode]
br.form["outboundDateString"] = outboundDate
# br.find_control(id="outboundTimeOfDay",name="outboundTimeOfDay").value = ['NOON_TO_6PM']
br.form["returnDateString"] = returnDate
br.find_control(id="roundTrip",name="twoWayTrip").value = ['false']
try:
	if(pointsFlag == True):
		br.find_control(name="fareType").value = ['POINTS']
	else:
		br.find_control(name="fareType").value = ['DOLLARS']
except:
	print "WARNING: Fare type selection is not accessible at the moment.\n"
result = br.submit()
content = result.read()
with open("southwest_results.html", "w") as f:
    f.write(content)

southwest_results_file = open("southwest_results.html", "r")
southwest_results_string = southwest_results_file.read()
parser = MyHTMLParser()

print originAirportName+" ---> "+destinationAirportName+" [ "+outboundDay+", "+outboundDate+" ]"
for x in range(1,30):
	inputPosBeg = southwest_results_string.find("<input id=\"Out"+str(x)+"C\"")
	if(inputPosBeg != -1):
		inputPosEnd = southwest_results_string.find("/>", inputPosBeg)
		outboundFlightResult = southwest_results_string[(inputPosBeg):(inputPosEnd+2)]
		parser.feed(outboundFlightResult)

		if(pointsFlag == True):
			inputPosBeg2 = southwest_results_string.find("<label", inputPosBeg)
			inputPosEnd2 = southwest_results_string.find("</label>", inputPosBeg2)
			outboundFlightResult = southwest_results_string[(inputPosBeg2):(inputPosEnd2+8)]
			parser.feed(outboundFlightResult)

		if(nonstopFlag and (temp.find("nonstop") == 0) ):
			print currentPrice+"\t"+departTime+"\t"+departTag+"\t"+arriveTime+"\t"+arriveTag+"\t(Flight # "+flightNum+")"+"\t"+route
		elif(nonstopFlag and (temp.find("nonstop") != 0) ):
			pass
		else:
			print currentPrice+"\t"+departTime+"\t"+departTag+"\t"+arriveTime+"\t"+arriveTag+"\t(Flight # "+flightNum+")"+"\t"+route

print ""

print destinationAirportName+" ---> "+originAirportName+" [ "+returnDay+", "+returnDate+" ]"
for x in range(1,30):
	inputPosBeg = southwest_results_string.find("<input id=\"In"+str(x)+"C\"")
	if(inputPosBeg != -1):
		inputPosEnd = southwest_results_string.find("/>", inputPosBeg)
		inboundFlightResult = southwest_results_string[(inputPosBeg):(inputPosEnd+2)]
		parser.feed(inboundFlightResult)
		
		if(pointsFlag == True):
			inputPosBeg2 = southwest_results_string.find("<label", inputPosBeg)
			inputPosEnd2 = southwest_results_string.find("</label>", inputPosBeg2)
			inboundFlightResult = southwest_results_string[(inputPosBeg2):(inputPosEnd2+8)]
			parser.feed(inboundFlightResult)

		if(nonstopFlag and (temp.find("nonstop") == 0) ):
			print currentPrice+"\t"+departTime+"\t"+departTag+"\t"+arriveTime+"\t"+arriveTag+"\t(Flight # "+flightNum+")"+"\t"+route
		elif(nonstopFlag and (temp.find("nonstop") != 0) ):
			pass
		else:
			print currentPrice+"\t"+departTime+"\t"+departTag+"\t"+arriveTime+"\t"+arriveTag+"\t(Flight # "+flightNum+")"+"\t"+route

print ""

# fare_reducer():
'''
"CAK":{
	"code":"CAK",
	"station_name":"Akron-Canton",
	"state_federal_unit":"OH",
	"country_code":"US",
	"airport_list_name":"Akron-Canton, OH - CAK",
	"display_name":"Akron-Canton, OH - CAK",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Ohio"
	},
"ALB":{
	"code":"ALB",
	"station_name":"Albany",
	"state_federal_unit":"NY",
	"country_code":"US",
	"airport_list_name":"Albany, NY - ALB",
	"display_name":"Albany, NY - ALB",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"New York"
	},
"ABQ":{
	"code":"ABQ",
	"station_name":"Albuquerque",
	"state_federal_unit":"NM",
	"country_code":"US",
	"airport_list_name":"Albuquerque, NM - ABQ",
	"display_name":"Albuquerque, NM - ABQ",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"New Mexico, Santa Fe"
	},
"AMA":{
	"code":"AMA",
	"station_name":"Amarillo",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"Amarillo, TX - AMA",
	"display_name":"Amarillo, TX - AMA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Texas"
	},
"AUA":{
	"code":"AUA",
	"station_name":"Aruba",
	"state_federal_unit":"Aruba",
	"country_code":"AW",
	"airport_list_name":"Aruba, Aruba - AUA",
	"display_name":"Aruba, Aruba - AUA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":""
	},
"ATL":{
	"code":"ATL",
	"station_name":"Atlanta",
	"state_federal_unit":"GA",
	"country_code":"US",
	"airport_list_name":"Atlanta, GA - ATL",
	"display_name":"Atlanta, GA - ATL",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Georgia, Giorgia"
	},
"AUS":{
	"code":"AUS",
	"station_name":"Austin",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"Austin, TX - AUS",
	"display_name":"Austin, TX - AUS",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Texas"
	},
"BWI":{
	"code":"BWI",
	"station_name":"Baltimore/Washington",
	"state_federal_unit":"MD",
	"country_code":"US",
	"airport_list_name":"Baltimore/Washington, MD - BWI",
	"display_name":"Baltimore/Washington, MD - BWI",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Maryland, District of Columbia, Balmo, Balmer, D.C., DC"
	},
"BZE":{
	"code":"BZE",
	"station_name":"Belize City",
	"state_federal_unit":"Belize",
	"country_code":"BZ",
	"airport_list_name":"Belize City, Belize - BZE",
	"display_name":"Belize City, Belize - BZE",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":""
	},
"BHM":{
	"code":"BHM",
	"station_name":"Birmingham",
	"state_federal_unit":"AL",
	"country_code":"US",
	"airport_list_name":"Birmingham, AL - BHM",
	"display_name":"Birmingham, AL - BHM",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Alabama, Tuscaloosa"
	},
"BOI":{
	"code":"BOI",
	"station_name":"Boise",
	"state_federal_unit":"ID",
	"country_code":"US",
	"airport_list_name":"Boise, ID - BOI",
	"display_name":"Boise, ID - BOI",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Idaho, Yellowstone"
	},
"BOT":{
	"code":"BOT",
	"station_name":"Boston Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"Boston Area",
	"display_name":"Boston Area, - BOT",
	"children":["BOS","MHT","PVD"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"BOS":{
	"code":"BOS",
	"station_name":"Boston Logan",
	"state_federal_unit":"MA",
	"country_code":"US",
	"airport_list_name":"Boston Logan, MA - BOS",
	"display_name":"Boston Logan, MA - BOS",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Massachusets, Providence, Beantown"
	},
"BUF":{
	"code":"BUF",
	"station_name":"Buffalo/Niagara",
	"state_federal_unit":"NY",
	"country_code":"US",
	"airport_list_name":"Buffalo/Niagara, NY - BUF",
	"display_name":"Buffalo/Niagara, NY - BUF",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"New York, Niagara Falls, Toronto"
	},
"BUR":{
	"code":"BUR",
	"station_name":"Burbank",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"Burbank, CA - BUR",
	"display_name":"Burbank, CA - BUR",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Hollywood, Los Angeles, Orange County, Santa Ana, Ontario, Universal Studios, Long Beach, LGB, Bob Hope"
	},
"SJD":{
	"code":"SJD",
	"station_name":"Cabo San Lucas/Los Cabos",
	"state_federal_unit":"MX",
	"country_code":"MX",
	"airport_list_name":"Cabo San Lucas/Los Cabos, MX - SJD",
	"display_name":"Cabo San Lucas/Los Cabos, MX - SJD",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Mexico"
	},
"CUN":{
	"code":"CUN",
	"station_name":"Cancun",
	"state_federal_unit":"Mexico",
	"country_code":"MX",
	"airport_list_name":"Cancun, Mexico - CUN",
	"display_name":"Cancun, Mexico - CUN",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Mexico"
	},
"CHS":{
	"code":"CHS",
	"station_name":"Charleston",
	"state_federal_unit":"SC",
	"country_code":"US",
	"airport_list_name":"Charleston, SC - CHS",
	"display_name":"Charleston, SC - CHS",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"South Carolina, Savannah, Myrtle Beach"
	},
"CLT":{
	"code":"CLT",
	"station_name":"Charlotte",
	"state_federal_unit":"NC",
	"country_code":"US",
	"airport_list_name":"Charlotte, NC - CLT",
	"display_name":"Charlotte, NC - CLT",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"North Carolina, Concord"
	},
"MDW":{
	"code":"MDW",
	"station_name":"Chicago (Midway)",
	"state_federal_unit":"IL",
	"country_code":"US",
	"airport_list_name":"Chicago (Midway), IL - MDW",
	"display_name":"Chicago (Midway), IL - MDW",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Illinois, Ilinois, Chitown, Windy City, ORD, Ohare, O'Hare"
	},
"CNN":{
	"code":"CNN",
	"station_name":"Cincinnati Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"Cincinnati Area",
	"display_name":"Cincinnati Area, - CNN",
	"children":["DAY"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"CLE":{
	"code":"CLE",
	"station_name":"Cleveland",
	"state_federal_unit":"OH",
	"country_code":"US",
	"airport_list_name":"Cleveland, OH - CLE",
	"display_name":"Cleveland, OH - CLE",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Ohio, Akron"
	},
"CVL":{
	"code":"CVL",
	"station_name":"Cleveland Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"Cleveland Area",
	"display_name":"Cleveland Area, - CVL",
	"children":["CAK","CLE"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"CMH":{
	"code":"CMH",
	"station_name":"Columbus",
	"state_federal_unit":"OH",
	"country_code":"US",
	"airport_list_name":"Columbus, OH - CMH",
	"display_name":"Columbus, OH - CMH",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Ohio"
	},
"CRP":{
	"code":"CRP",
	"station_name":"Corpus Christi",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"Corpus Christi, TX - CRP",
	"display_name":"Corpus Christi, TX - CRP",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Texas"
	},
"DAL":{
	"code":"DAL",
	"station_name":"Dallas (Love Field)",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"Dallas (Love Field), TX - DAL",
	"display_name":"Dallas (Love Field), TX - DAL",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"DFW, Ft. Worth, Fort Worth, Texas"
	},
"DAY":{
	"code":"DAY",
	"station_name":"Dayton",
	"state_federal_unit":"OH",
	"country_code":"US",
	"airport_list_name":"Dayton, OH - DAY",
	"display_name":"Dayton, OH - DAY",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Ohio, Cincinnati, Columbus, CVG"
	},
"DEN":{
	"code":"DEN",
	"station_name":"Denver",
	"state_federal_unit":"CO",
	"country_code":"US",
	"airport_list_name":"Denver, CO - DEN",
	"display_name":"Denver, CO - DEN",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Colorado, Boulder, Aspen, Vail, Colorado Springs, Mile High City, Skiing"
	},
"DSM":{
	"code":"DSM",
	"station_name":"Des Moines",
	"state_federal_unit":"IA",
	"country_code":"US",
	"airport_list_name":"Des Moines, IA - DSM",
	"display_name":"Des Moines, IA - DSM",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Iowa"
	},
"DTW":{
	"code":"DTW",
	"station_name":"Detroit",
	"state_federal_unit":"MI",
	"country_code":"US",
	"airport_list_name":"Detroit, MI - DTW",
	"display_name":"Detroit, MI - DTW",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":""
	},
"ELP":{
	"code":"ELP",
	"station_name":"El Paso",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"El Paso, TX - ELP",
	"display_name":"El Paso, TX - ELP",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Texas, Ciudad Juarez"
	},
"FNT":{
	"code":"FNT",
	"station_name":"Flint",
	"state_federal_unit":"MI",
	"country_code":"US",
	"airport_list_name":"Flint, MI - FNT",
	"display_name":"Flint, MI - FNT",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Michigan, Lausing, East Lansing"
	},
"FLL":{
	"code":"FLL",
	"station_name":"Ft. Lauderdale",
	"state_federal_unit":"FL",
	"country_code":"US",
	"airport_list_name":"Ft. Lauderdale, FL - FLL",
	"display_name":"Ft. Lauderdale, FL - FLL",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Florida, MIA, Coral Gables, Miami, Boca Raton, West Palm Beach, Ft Lauderdale, Fort Lauderdale"
	},
"RSW":{
	"code":"RSW",
	"station_name":"Ft. Myers",
	"state_federal_unit":"FL",
	"country_code":"US",
	"airport_list_name":"Ft. Myers, FL - RSW",
	"display_name":"Ft. Myers, FL - RSW",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Ft. Myers, Florida, Cape Coral, Ft. Meyers, Fort Meyers, Naples"
	},
"GRR":{
	"code":"GRR",
	"station_name":"Grand Rapids",
	"state_federal_unit":"MI",
	"country_code":"US",
	"airport_list_name":"Grand Rapids, MI - GRR",
	"display_name":"Grand Rapids, MI - GRR",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Michigan, Lausing, East Lansing"
	},
"GSP":{
	"code":"GSP",
	"station_name":"Greenville/Spartanburg",
	"state_federal_unit":"SC",
	"country_code":"US",
	"airport_list_name":"Greenville/Spartanburg, SC - GSP",
	"display_name":"Greenville/Spartanburg, SC - GSP",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":""
	},
"HRL":{
	"code":"HRL",
	"station_name":"Harlingen",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"Harlingen, TX - HRL",
	"display_name":"Harlingen, TX - HRL",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Texas, McAllen, South Padre"
	},
"BDL":{
	"code":"BDL",
	"station_name":"Hartford",
	"state_federal_unit":"CT",
	"country_code":"US",
	"airport_list_name":"Hartford, CT - BDL",
	"display_name":"Hartford, CT - BDL",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Connecticut, New Haven"
	},
"HOU":{
	"code":"HOU",
	"station_name":"Houston (Hobby)",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"Houston (Hobby), TX - HOU",
	"display_name":"Houston (Hobby), TX - HOU",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Texas, HUO, IAH, George Bush International, Galveston, H-Town, Huoston"
	},
"IND":{
	"code":"IND",
	"station_name":"Indianapolis",
	"state_federal_unit":"IN",
	"country_code":"US",
	"airport_list_name":"Indianapolis, IN - IND",
	"display_name":"Indianapolis, IN - IND",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Indiana, Dayton"
	},
"JAX":{
	"code":"JAX",
	"station_name":"Jacksonville",
	"state_federal_unit":"FL",
	"country_code":"US",
	"airport_list_name":"Jacksonville, FL - JAX",
	"display_name":"Jacksonville, FL - JAX",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Florida"
	},
"MCI":{
	"code":"MCI",
	"station_name":"Kansas City",
	"state_federal_unit":"MO",
	"country_code":"US",
	"airport_list_name":"Kansas City, MO - MCI",
	"display_name":"Kansas City, MO - MCI",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Kansas, Wheeler, Show Me, Missouri"
	},
"LAS":{
	"code":"LAS",
	"station_name":"Las Vegas",
	"state_federal_unit":"NV",
	"country_code":"US",
	"airport_list_name":"Las Vegas, NV - LAS",
	"display_name":"Las Vegas, NV - LAS",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Nevada, Sin City, The Strip, Los Vegas"
	},
"LIR":{
	"code":"LIR",
	"station_name":"Liberia",
	"state_federal_unit":"Costa Rica",
	"country_code":"CR",
	"airport_list_name":"Liberia, Costa Rica - LIR",
	"display_name":"Liberia, Costa Rica - LIR",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":""
	},
"LIT":{
	"code":"LIT",
	"station_name":"Little Rock",
	"state_federal_unit":"AR",
	"country_code":"US",
	"airport_list_name":"Little Rock, AR - LIT",
	"display_name":"Little Rock, AR - LIT",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Arkansas, Jacksonville, Hot Springs"
	},
"ISP":{
	"code":"ISP",
	"station_name":"Long Island/Islip",
	"state_federal_unit":"NY",
	"country_code":"US",
	"airport_list_name":"Long Island/Islip, NY - ISP",
	"display_name":"Long Island/Islip, NY - ISP",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"New York, Queens, JFK"
	},
"LAX":{
	"code":"LAX",
	"station_name":"Los Angeles",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"Los Angeles, CA - LAX",
	"display_name":"Los Angeles, CA - LAX",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Irvine, Long Beach, Hollywood, Palm Springs, Malibu, City of Angels, Las Angeles, Disney, Burbank, Orange County, Santa Ana, Ontario, Universal Studios, LGB"
	},
"LOS":{
	"code":"LOS",
	"station_name":"Los Angeles Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"Los Angeles Area",
	"display_name":"Los Angeles Area, - LOS",
	"children":["BUR","LAX","ONT","SNA"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"SDF":{
	"code":"SDF",
	"station_name":"Louisville",
	"state_federal_unit":"KY",
	"country_code":"US",
	"airport_list_name":"Louisville, KY - SDF",
	"display_name":"Louisville, KY - SDF",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Kentucky, Lexington, Frankfort"
	},
"LBB":{
	"code":"LBB",
	"station_name":"Lubbock",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"Lubbock, TX - LBB",
	"display_name":"Lubbock, TX - LBB",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Texas"
	},
"MHT":{
	"code":"MHT",
	"station_name":"Manchester",
	"state_federal_unit":"NH",
	"country_code":"US",
	"airport_list_name":"Manchester, NH - MHT",
	"display_name":"Manchester, NH - MHT",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"New Hampshire, Portsmouth"
	},
"MEM":{
	"code":"MEM",
	"station_name":"Memphis",
	"state_federal_unit":"TN",
	"country_code":"US",
	"airport_list_name":"Memphis, TN - MEM",
	"display_name":"Memphis, TN - MEM",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Tennessee"
	},
"MEX":{
	"code":"MEX",
	"station_name":"Mexico City",
	"state_federal_unit":"Mexico",
	"country_code":"MX",
	"airport_list_name":"Mexico City, Mexico - MEX",
	"display_name":"Mexico City, Mexico - MEX",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":""
	},
"MMA":{
	"code":"MMA",
	"station_name":"Miami Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"Miami Area",
	"display_name":"Miami Area, - MMA",
	"children":["FLL"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"MAF":{
	"code":"MAF",
	"station_name":"Midland/Odessa",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"Midland/Odessa, TX - MAF",
	"display_name":"Midland/Odessa, TX - MAF",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Texas"
	},
"MKE":{
	"code":"MKE",
	"station_name":"Milwaukee",
	"state_federal_unit":"WI",
	"country_code":"US",
	"airport_list_name":"Milwaukee, WI - MKE",
	"display_name":"Milwaukee, WI - MKE",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Wisconsin"
	},
"MSP":{
	"code":"MSP",
	"station_name":"Minneapolis/St. Paul (Terminal 2)",
	"state_federal_unit":"MN",
	"country_code":"US",
	"airport_list_name":"Minneapolis/St. Paul (Terminal 2), MN - MSP",
	"display_name":"Minneapolis/St. Paul (Terminal 2), MN - MSP",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Minnesota, Twin Cities"
	},
"MBJ":{
	"code":"MBJ",
	"station_name":"Montego Bay",
	"state_federal_unit":"Jamaica",
	"country_code":"JM",
	"airport_list_name":"Montego Bay, Jamaica - MBJ",
	"display_name":"Montego Bay, Jamaica - MBJ",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Jamaica"
	},
"BNA":{
	"code":"BNA",
	"station_name":"Nashville",
	"state_federal_unit":"TN",
	"country_code":"US",
	"airport_list_name":"Nashville, TN - BNA",
	"display_name":"Nashville, TN - BNA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Tennessee"
	},
"NAS":{
	"code":"NAS",
	"station_name":"Nassau",
	"state_federal_unit":"Bahamas",
	"country_code":"BS",
	"airport_list_name":"Nassau, Bahamas - NAS",
	"display_name":"Nassau, Bahamas - NAS",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Bahamas"
	},
"MSY":{
	"code":"MSY",
	"station_name":"New Orleans",
	"state_federal_unit":"LA",
	"country_code":"US",
	"airport_list_name":"New Orleans, LA - MSY",
	"display_name":"New Orleans, LA - MSY",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Louisiana, Luoisiana, Baton Rouge, The Big Easy, The Cresent City, Bourbon St., Spring Break"
	},
"NWY":{
	"code":"NWY",
	"station_name":"New York Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"New York Area",
	"display_name":"New York Area, - NWY",
	"children":["ISP","LGA","EWR"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"LGA":{
	"code":"LGA",
	"station_name":"New York (LaGuardia)",
	"state_federal_unit":"NY",
	"country_code":"US",
	"airport_list_name":"New York (LaGuardia), NY - LGA",
	"display_name":"New York (LaGuardia), NY - LGA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"New York, Manhattan, Bronx, New Jersey, NYC, Queens, Brooklyn, The Big Apple, Empire State, Times Square, JFK"
	},
"EWR":{
	"code":"EWR",
	"station_name":"New York/Newark",
	"state_federal_unit":"NJ",
	"country_code":"US",
	"airport_list_name":"New York/Newark, NJ - EWR",
	"display_name":"New York/Newark, NJ - EWR",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"New York, Manhattan, Bronx, New Jersey, NYC, Queens, Brooklyn, The Big Apple, Empire State, Times Square, JFK"
	},
"ORF":{
	"code":"ORF",
	"station_name":"Norfolk",
	"state_federal_unit":"VA",
	"country_code":"US",
	"airport_list_name":"Norfolk, VA - ORF",
	"display_name":"Norfolk, VA - ORF",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Virginia, Newport News"
	},
"NFB":{
	"code":"NFB",
	"station_name":"Northwest Florida Beaches Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"Northwest Florida Beaches Area",
	"display_name":"Northwest Florida Beaches Area, - NFB",
	"children":["ECP","PNS"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"OAK":{
	"code":"OAK",
	"station_name":"Oakland",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"Oakland, CA - OAK",
	"display_name":"Oakland, CA - OAK",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Fremont, Bay"
	},
"OKC":{
	"code":"OKC",
	"station_name":"Oklahoma City",
	"state_federal_unit":"OK",
	"country_code":"US",
	"airport_list_name":"Oklahoma City, OK - OKC",
	"display_name":"Oklahoma City, OK - OKC",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Oklahoma, Stillwater, Tulsa, Norman"
	},
"OMA":{
	"code":"OMA",
	"station_name":"Omaha",
	"state_federal_unit":"NE",
	"country_code":"US",
	"airport_list_name":"Omaha, NE - OMA",
	"display_name":"Omaha, NE - OMA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Nebraska"
	},
"ONT":{
	"code":"ONT",
	"station_name":"Ontario/LA",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"Ontario/LA, CA - ONT",
	"display_name":"Ontario/LA, CA - ONT",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Los Angeles, San Bernardino, Las Angeles, Orange County, Santa Ana, Ontario, Universal Studios, Long Beach, LGB"
	},
"SNA":{
	"code":"SNA",
	"station_name":"Orange County/Santa Ana",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"Orange County/Santa Ana, CA - SNA",
	"display_name":"Orange County/Santa Ana, CA - SNA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Irvine, Los Angeles, Las Angeles, Ontario, Orange County, Santa Ana, Universal Studios, Long Beach, LGB, John Wayne"
	},
"MCO":{
	"code":"MCO",
	"station_name":"Orlando",
	"state_federal_unit":"FL",
	"country_code":"US",
	"airport_list_name":"Orlando, FL - MCO",
	"display_name":"Orlando, FL - MCO",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Florida, Tampa, Disney, Universal Studios, SeaWorld, Sea World"
	},
"ECP":{
	"code":"ECP",
	"station_name":"Panama City Beach",
	"state_federal_unit":"FL",
	"country_code":"US",
	"airport_list_name":"Panama City Beach, FL - ECP",
	"display_name":"Panama City Beach, FL - ECP",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Florida, Tallahassee, Destin, Spring Break"
	},
"PNS":{
	"code":"PNS",
	"station_name":"Pensacola",
	"state_federal_unit":"FL",
	"country_code":"US",
	"airport_list_name":"Pensacola, FL - PNS",
	"display_name":"Pensacola, FL - PNS",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Florida, Destin, Spring Break, Mobile"
	},
"PHL":{
	"code":"PHL",
	"station_name":"Philadelphia",
	"state_federal_unit":"PA",
	"country_code":"US",
	"airport_list_name":"Philadelphia, PA - PHL",
	"display_name":"Philadelphia, PA - PHL",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Pennsylvannia, New Jersey, Atlantic City, Philly"
	},
"PHX":{
	"code":"PHX",
	"station_name":"Phoenix",
	"state_federal_unit":"AZ",
	"country_code":"US",
	"airport_list_name":"Phoenix, AZ - PHX",
	"display_name":"Phoenix, AZ - PHX",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Arizona, Tucson, Sedona, Grand Canyon"
	},
"PIT":{
	"code":"PIT",
	"station_name":"Pittsburgh",
	"state_federal_unit":"PA",
	"country_code":"US",
	"airport_list_name":"Pittsburgh, PA - PIT",
	"display_name":"Pittsburgh, PA - PIT",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Pennsylvania"
	},
"PDX":{
	"code":"PDX",
	"station_name":"Portland",
	"state_federal_unit":"OR",
	"country_code":"US",
	"airport_list_name":"Portland, OR - PDX",
	"display_name":"Portland, OR - PDX",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Stumptown, Oregon, Beaverton"
	},
"PWM":{
	"code":"PWM",
	"station_name":"Portland",
	"state_federal_unit":"ME",
	"country_code":"US",
	"airport_list_name":"Portland, ME - PWM",
	"display_name":"Portland, ME - PWM",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Maine"
	},
"PVD":{
	"code":"PVD",
	"station_name":"Providence",
	"state_federal_unit":"RI",
	"country_code":"US",
	"airport_list_name":"Providence, RI - PVD",
	"display_name":"Providence, RI - PVD",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Rhode Island, Massachusetts, Connecticut"
	},
"PVR":{
	"code":"PVR",
	"station_name":"Puerto Vallarta",
	"state_federal_unit":"MX",
	"country_code":"MX",
	"airport_list_name":"Puerto Vallarta, MX - PVR",
	"display_name":"Puerto Vallarta, MX - PVR",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":""
	},
"PUJ":{
	"code":"PUJ",
	"station_name":"Punta Cana",
	"state_federal_unit":"DR",
	"country_code":"DR",
	"airport_list_name":"Punta Cana, DR - PUJ",
	"display_name":"Punta Cana, DR - PUJ",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Dominican Republic"
	},
"RDU":{
	"code":"RDU",
	"station_name":"Raleigh/Durham",
	"state_federal_unit":"NC",
	"country_code":"US",
	"airport_list_name":"Raleigh/Durham, NC - RDU",
	"display_name":"Raleigh/Durham, NC - RDU",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"North Carolina, Chapel Hill, Greensboro"
	},
"RNO":{
	"code":"RNO",
	"station_name":"Reno/Tahoe",
	"state_federal_unit":"NV",
	"country_code":"US",
	"airport_list_name":"Reno/Tahoe, NV - RNO",
	"display_name":"Reno/Tahoe, NV - RNO",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Nevada, Lake Tahoe, Carson City"
	},
"RIC":{
	"code":"RIC",
	"station_name":"Richmond",
	"state_federal_unit":"VA",
	"country_code":"US",
	"airport_list_name":"Richmond, VA - RIC",
	"display_name":"Richmond, VA - RIC",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Virginia"
	},
"ROC":{
	"code":"ROC",
	"station_name":"Rochester",
	"state_federal_unit":"NY",
	"country_code":"US",
	"airport_list_name":"Rochester, NY - ROC",
	"display_name":"Rochester, NY - ROC",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"New York, Syracuse, Toronto"
	},
"SMF":{
	"code":"SMF",
	"station_name":"Sacramento",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"Sacramento, CA - SMF",
	"display_name":"Sacramento, CA - SMF",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Napa, Yosemite"
	},
"SLC":{
	"code":"SLC",
	"station_name":"Salt Lake City",
	"state_federal_unit":"UT",
	"country_code":"US",
	"airport_list_name":"Salt Lake City, UT - SLC",
	"display_name":"Salt Lake City, UT - SLC",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Utah, Provo, Skiing, Yellowstone"
	},
"SAT":{
	"code":"SAT",
	"station_name":"San Antonio",
	"state_federal_unit":"TX",
	"country_code":"US",
	"airport_list_name":"San Antonio, TX - SAT",
	"display_name":"San Antonio, TX - SAT",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Alamo City, Texas, SeaWorld, Sea World"
	},
"SAN":{
	"code":"SAN",
	"station_name":"San Diego",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"San Diego, CA - SAN",
	"display_name":"San Diego, CA - SAN",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Tijuana, SeaWorld, Sea World"
	},
"SFO":{
	"code":"SFO",
	"station_name":"San Francisco",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"San Francisco, CA - SFO",
	"display_name":"San Francisco, CA - SFO",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Napa, San Mateo, Frisco, Golden Gate City, Bay"
	},
"SFC":{
	"code":"SFC",
	"station_name":"San Francisco Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"San Francisco Area",
	"display_name":"San Francisco Area, - SFC",
	"children":["OAK","SFO","SJC"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"SJC":{
	"code":"SJC",
	"station_name":"San Jose",
	"state_federal_unit":"CA",
	"country_code":"US",
	"airport_list_name":"San Jose, CA - SJC",
	"display_name":"San Jose, CA - SJC",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"California, Silicon Valley, Carmel, San Hose, Bay"
	},
"SJO":{
	"code":"SJO",
	"station_name":"San Jose",
	"state_federal_unit":"Costa Rica",
	"country_code":"CR",
	"airport_list_name":"San Jose, Costa Rica - SJO",
	"display_name":"San Jose, Costa Rica - SJO",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"San Hose"
	},
"SJU":{
	"code":"SJU",
	"station_name":"San Juan",
	"state_federal_unit":"PR",
	"country_code":"US",
	"airport_list_name":"San Juan, PR - SJU",
	"display_name":"San Juan, PR - SJU",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Puerto Rico"
	},
"SEA":{
	"code":"SEA",
	"station_name":"Seattle/Tacoma",
	"state_federal_unit":"WA",
	"country_code":"US",
	"airport_list_name":"Seattle/Tacoma, WA - SEA",
	"display_name":"Seattle/Tacoma, WA - SEA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Emerald City, Washington, Vancouver"
	},
"GEG":{
	"code":"GEG",
	"station_name":"Spokane",
	"state_federal_unit":"WA",
	"country_code":"US",
	"airport_list_name":"Spokane, WA - GEG",
	"display_name":"Spokane, WA - GEG",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Washington"
	},
"STL":{
	"code":"STL",
	"station_name":"St. Louis",
	"state_federal_unit":"MO",
	"country_code":"US",
	"airport_list_name":"St. Louis, MO - STL",
	"display_name":"St. Louis, MO - STL",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Missouri, Saint Louis, St. Luois"
	},
"TPA":{
	"code":"TPA",
	"station_name":"Tampa",
	"state_federal_unit":"FL",
	"country_code":"US",
	"airport_list_name":"Tampa, FL - TPA",
	"display_name":"Tampa, FL - TPA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Florida, Orlando, Bay, Bush Gardens, Busch Gardens"
	},
"TUS":{
	"code":"TUS",
	"station_name":"Tucson",
	"state_federal_unit":"AZ",
	"country_code":"US",
	"airport_list_name":"Tucson, AZ - TUS",
	"display_name":"Tucson, AZ - TUS",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Arizona"
	},
"TUL":{
	"code":"TUL",
	"station_name":"Tulsa",
	"state_federal_unit":"OK",
	"country_code":"US",
	"airport_list_name":"Tulsa, OK - TUL",
	"display_name":"Tulsa, OK - TUL",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Oklahoma, Stillwater"
	},
"IAD":{
	"code":"IAD",
	"station_name":"Washington (Dulles)",
	"state_federal_unit":"DC",
	"country_code":"US",
	"airport_list_name":"Washington (Dulles), DC - IAD",
	"display_name":"Washington (Dulles), DC - IAD",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Capital City, America Capital, District of Columbia, DC, D.C."
	},
"DCA":{
	"code":"DCA",
	"station_name":"Washington (Reagan National)",
	"state_federal_unit":"DC",
	"country_code":"US",
	"airport_list_name":"Washington (Reagan National), DC - DCA",
	"display_name":"Washington (Reagan National), DC - DCA",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Capital City, America Capital, District of Columbia, DC, D.C."
	},
"WDC":{
	"code":"WDC",
	"station_name":"Washington, D.C. Area",
	"state_federal_unit":"",
	"country_code":"",
	"airport_list_name":"Washington, D.C. Area",
	"display_name":"Washington, D.C. Area, - WDC",
	"children":["BWI","IAD","DCA"],
	"mkt_carrier_codes":[],
	"alt_search_names":""
	},
"PBI":{
	"code":"PBI",
	"station_name":"West Palm Beach",
	"state_federal_unit":"FL",
	"country_code":"US",
	"airport_list_name":"West Palm Beach, FL - PBI",
	"display_name":"West Palm Beach, FL - PBI",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Florida, Boca Raton, Port St. Lucie"
	},
"ICT":{
	"code":"ICT",
	"station_name":"Wichita",
	"state_federal_unit":"KS",
	"country_code":"US",
	"airport_list_name":"Wichita, KS - ICT",
	"display_name":"Wichita, KS - ICT",
	"children":[],	
	"mkt_carrier_codes":["WN"],
	"alt_search_names":"Kansas"
	}}
'''
