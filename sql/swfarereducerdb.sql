/* ********************************** START *********************************** */

START TRANSACTION;

/* **************************************************************************** */
/* ****************************** CREATE DATABASE ****************************** */

DROP DATABASE IF EXISTS SWFAREREDUCERDB;

CREATE DATABASE IF NOT EXISTS SWFAREREDUCERDB CHARACTER SET utf8 COLLATE utf8_general_ci;

USE SWFAREREDUCERDB;

/* ****************************************************************************** */
/* ******************************** CREATE TABLE ******************************** */
CREATE TABLE IF NOT EXISTS WIRELESS_CARRIERS (
WIRELESS_CARRIER_ID			INT(11) NOT NULL AUTO_INCREMENT,
CARRIER_NAME				VARCHAR(255) NOT NULL,
CARRIER_TEXT_EMAIL			VARCHAR(255) NOT NULL,
PRIMARY KEY (WIRELESS_CARRIER_ID),
UNIQUE (CARRIER_NAME)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='WIRELESS CARRIERS' AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS AIRPORTS (
AIRPORT_ID					INT(11) NOT NULL AUTO_INCREMENT,
AIRPORT_CODE 				VARCHAR(3) NOT NULL,
AIRPORT_NAME				VARCHAR(255) DEFAULT NULL,
ROUTES_SERVED				VARCHAR(1023) DEFAULT NULL,
UPDATE_TIMESTAMP			TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
INSERT_TIMESTAMP			TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (AIRPORT_ID),
UNIQUE (AIRPORT_CODE)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='AIRPORTS' AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS UPCOMING_FLIGHTS (
UPCOMING_FLIGHT_ID			INT(11) NOT NULL AUTO_INCREMENT,
DEPART_AIRPORT_CODE     	VARCHAR(3) DEFAULT NULL,
ARRIVE_AIRPORT_CODE			VARCHAR(3) DEFAULT NULL,
DEPART_DATE_TIME			TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
ARRIVE_DATE_TIME			TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
FLIGHT_NUM					VARCHAR(9) DEFAULT NULL,
FLIGHT_ROUTE				VARCHAR(30) DEFAULT NULL,
FARE_PRICE_DOLLARS			INT(10) NOT NULL DEFAULT 0,
FARE_PRICE_POINTS			INT(10) NOT NULL DEFAULT 0,
FARE_TYPE					VARCHAR(15) NOT NULL DEFAULT 'Wanna Get Away',
UPDATE_TIMESTAMP			TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
INSERT_TIMESTAMP			TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (UPCOMING_FLIGHT_ID),
UNIQUE (DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE_TIME,FLIGHT_NUM)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='UPCOMING FLIGHTS' AUTO_INCREMENT=100000;

CREATE TABLE IF NOT EXISTS RESERVED_FLIGHTS (
RESERVED_FLIGHT_ID			INT(11) NOT NULL AUTO_INCREMENT,
CONFIRMATION_NUM			VARCHAR(6) NOT NULL,
FIRST_NAME					VARCHAR(255) NOT NULL,
LAST_NAME					VARCHAR(255) NOT NULL,
EMAIL						VARCHAR(255) DEFAULT NULL,
PHONE_NUM					INT(10) DEFAULT NULL,
WIRELESS_CARRIER_ID			INT(11) DEFAULT NULL,
UPCOMING_FLIGHT_ID			INT(11) NOT NULL,
FARE_LABEL					VARCHAR(7) NOT NULL DEFAULT 'DOLLARS',
FARE_PRICE_PAID				INT(10) NOT NULL DEFAULT 0,
FARE_TYPE					VARCHAR(15) NOT NULL DEFAULT 'Wanna Get Away',
ALERT_TIMESTAMP				TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
UPDATE_TIMESTAMP			TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
INSERT_TIMESTAMP			TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (RESERVED_FLIGHT_ID),
FOREIGN KEY (UPCOMING_FLIGHT_ID) REFERENCES UPCOMING_FLIGHTS(UPCOMING_FLIGHT_ID),
FOREIGN KEY (WIRELESS_CARRIER_ID) REFERENCES WIRELESS_CARRIERS(WIRELESS_CARRIER_ID),
UNIQUE (CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,UPCOMING_FLIGHT_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='RESERVED FLIGHTS' AUTO_INCREMENT=100000;

/* ***************************************************************************** */
/* ******************************** INSERT INTO ******************************** */

INSERT INTO WIRELESS_CARRIERS (CARRIER_NAME,CARRIER_TEXT_EMAIL) VALUES
('Alltel','@message.alltel.com'),
('AT&T','@txt.att.net'),
('Boost Mobile','@myboostmobile.com'),
('Cricket Wireless','@sms.mycricket.com'),
('MetroPCS','@MyMetroPcs.com'),
('Nextel','@messaging.nextel.com'),
('Sprint','@messaging.sprintpcs.com'),
('T-Mobile','@tmomail.net'),
('Ting','@message.ting.com'),
('U.S. Cellular','@email.uscc.net'),
('Verizon Wireless','@vtext.com'),
('Virgin Mobile','@vmobl.com');

INSERT INTO UPCOMING_FLIGHTS (DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE_TIME,ARRIVE_DATE_TIME,FLIGHT_NUM,FLIGHT_ROUTE,FARE_PRICE_DOLLARS,FARE_PRICE_POINTS,FARE_TYPE,UPDATE_TIMESTAMP) VALUES 
('SJC','ONT','2015-12-26 07:30:00','2015-12-26 08:40:00','5897','Nonstop','120','6862','Wanna Get Away','2015-11-30 12:30:00'),
('ONT','SJC','2015-12-29 06:10:00','2015-12-29 07:25:00','3117','Nonstop','65','3476','Wanna Get Away','2015-11-30 12:30:00');

INSERT INTO RESERVED_FLIGHTS (CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,EMAIL,PHONE_NUM,WIRELESS_CARRIER_ID,UPCOMING_FLIGHT_ID,FARE_LABEL,FARE_PRICE_PAID,FARE_TYPE) VALUES 
('RTG7KW','DANIELLE','GONZALEZ','NULL','9095698490','2','100000','DOLLARS','100','Wanna Get Away'),
('RTG7KW','DANIELLE','GONZALEZ','NULL','9095698490','2','100001','DOLLARS','65','Wanna Get Away');

INSERT INTO AIRPORTS (AIRPORT_CODE,AIRPORT_NAME) VALUES
('CAK','Akron-Canton, OH - CAK'),
('ALB','Albany, NY - ALB'),
('ABQ','Albuquerque, NM - ABQ'),
('AMA','Amarillo, TX - AMA'),
('AUA','Aruba, Aruba - AUA'),
('ATL','Atlanta, GA - ATL'),
('AUS','Austin, TX - AUS'),
('BWI','Baltimore/Washington, MD - BWI'),
('BZE','Belize City, Belize - BZE'),
('BHM','Birmingham, AL - BHM'),
('BOI','Boise, ID - BOI'),
('BOS','Boston Logan, MA - BOS'),
('BUF','Buffalo/Niagara, NY - BUF'),
('BUR','Burbank, CA - BUR'),
('SJD','Cabo San Lucas/Los Cabos, MX - SJD'),
('CUN','Cancun, Mexico - CUN'),
('CHS','Charleston, SC - CHS'),
('CLT','Charlotte, NC - CLT'),
('MDW','Chicago (Midway), IL - MDW'),
('CLE','Cleveland, OH - CLE'),
('CMH','Columbus, OH - CMH'),
('CRP','Corpus Christi, TX - CRP'),
('DAL','Dallas (Love Field), TX - DAL'),
('DAY','Dayton, OH - DAY'),
('DEN','Denver, CO - DEN'),
('DSM','Des Moines, IA - DSM'),
('DTW','Detroit, MI - DTW'),
('ELP','El Paso, TX - ELP'),
('FNT','Flint, MI - FNT'),
('FLL','Ft. Lauderdale, FL - FLL'),
('RSW','Ft. Myers, FL - RSW'),
('GRR','Grand Rapids, MI - GRR'),
('GSP','Greenville/Spartanburg, SC - GSP'),
('HRL','Harlingen, TX - HRL'),
('BDL','Hartford, CT - BDL'),
('HOU','Houston (Hobby), TX - HOU'),
('IND','Indianapolis, IN - IND'),
('JAX','Jacksonville, FL - JAX'),
('MCI','Kansas City, MO - MCI'),
('LAS','Las Vegas, NV - LAS'),
('LIR','Liberia, Costa Rica - LIR'),
('LIT','Little Rock, AR - LIT'),
('ISP','Long Island/Islip, NY - ISP'),
('LAX','Los Angeles, CA - LAX'),
('SDF','Louisville, KY - SDF'),
('LBB','Lubbock, TX - LBB'),
('MHT','Manchester, NH - MHT'),
('MEM','Memphis, TN - MEM'),
('MEX','Mexico City, Mexico - MEX'),
('MAF','Midland/Odessa, TX - MAF'),
('MKE','Milwaukee, WI - MKE'),
('MSP','Minneapolis/St. Paul (Terminal 2), MN - MSP'),
('MBJ','Montego Bay, Jamaica - MBJ'),
('BNA','Nashville, TN - BNA'),
('NAS','Nassau, Bahamas - NAS'),
('MSY','New Orleans, LA - MSY'),
('LGA','New York (LaGuardia), NY - LGA'),
('EWR','New York/Newark, NJ - EWR'),
('ORF','Norfolk, VA - ORF'),
('OAK','Oakland, CA - OAK'),
('OKC','Oklahoma City, OK - OKC'),
('OMA','Omaha, NE - OMA'),
('ONT','Ontario/LA, CA - ONT'),
('SNA','Orange County/Santa Ana, CA - SNA'),
('MCO','Orlando, FL - MCO'),
('ECP','Panama City Beach, FL - ECP'),
('PNS','Pensacola, FL - PNS'),
('PHL','Philadelphia, PA - PHL'),
('PHX','Phoenix, AZ - PHX'),
('PIT','Pittsburgh, PA - PIT'),
('PWM','Portland, ME - PWM'),
('PDX','Portland, OR - PDX'),
('PVD','Providence, RI - PVD'),
('PVR','Puerto Vallarta, MX - PVR'),
('PUJ','Punta Cana, DR - PUJ'),
('RDU','Raleigh/Durham, NC - RDU'),
('RNO','Reno/Tahoe, NV - RNO'),
('RIC','Richmond, VA - RIC'),
('ROC','Rochester, NY - ROC'),
('SMF','Sacramento, CA - SMF'),
('SLC','Salt Lake City, UT - SLC'),
('SAT','San Antonio, TX - SAT'),
('SAN','San Diego, CA - SAN'),
('SFO','San Francisco, CA - SFO'),
('SJC','San Jose, CA - SJC'),
('SJO','San Jose, Costa Rica - SJO'),
('SJU','San Juan, PR - SJU'),
('SEA','Seattle/Tacoma, WA - SEA'),
('GEG','Spokane, WA - GEG'),
('STL','St. Louis, MO - STL'),
('TPA','Tampa, FL - TPA'),
('TUS','Tucson, AZ - TUS'),
('TUL','Tulsa, OK - TUL'),
('IAD','Washington (Dulles), DC - IAD'),
('DCA','Washington (Reagan National), DC - DCA'),
('PBI','West Palm Beach, FL - PBI'),
('ICT','Wichita, KS - ICT');

/* ********************************** COMMIT ********************************** */

COMMIT WORK;

/* **************************************************************************** */
