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
AIRPORT_CITY				VARCHAR(255) DEFAULT NULL,
AIRPORT_NAME				VARCHAR(255) DEFAULT NULL,
AIRPORT_LATITUDE			VARCHAR(12) DEFAULT NULL,
AIRPORT_LONGITUDE			VARCHAR(12) DEFAULT NULL,
AIRPORT_TIMEZONE			VARCHAR(255) DEFAULT NULL,
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
PHONE_NUM					BIGINT(10) DEFAULT NULL,
WIRELESS_CARRIER_ID			INT(11) DEFAULT NULL,
UPCOMING_FLIGHT_ID			INT(11) NOT NULL,
FARE_LABEL					VARCHAR(7) NOT NULL DEFAULT 'DOLLARS',
FARE_PRICE_PAID				INT(10) NOT NULL DEFAULT 0,
FARE_TYPE					VARCHAR(15) NOT NULL DEFAULT 'Wanna Get Away',
FARE_PRICE_ALERT			TINYINT(1) NOT NULL DEFAULT 0,
CHECKIN_ALERT				TINYINT(1) NOT NULL DEFAULT 0,
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
('SJC','ONT','2015-12-26 07:30:00','2015-12-26 08:40:00','5897','Nonstop','120','6862','Wanna Get Away','2015-12-08 10:30:00'),
('ONT','SJC','2015-12-29 06:10:00','2015-12-29 07:25:00','3117','Nonstop','65','3476','Wanna Get Away','2015-12-08 10:30:00'),
('SJC','MSY','2016-02-06 07:00:00','2016-02-06 15:20:00','3660/3287','1 stop Change Planes in LAS','221','12918','Wanna Get Away','2015-12-08 10:30:00'),
('MSY','SJC','2016-02-09 18:20:00','2016-02-09 22:40:00','2599/1569','1 stop Change Planes in LAX','192','11029','Wanna Get Away','2015-12-08 10:30:00');

INSERT INTO RESERVED_FLIGHTS (CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,PHONE_NUM,WIRELESS_CARRIER_ID,UPCOMING_FLIGHT_ID,FARE_LABEL,FARE_PRICE_PAID,FARE_TYPE,UPDATE_TIMESTAMP) VALUES 
-- ('RTG7KW','DANIELLE','GONZALEZ','9095698490','2','100000','DOLLARS','100','Wanna Get Away','2015-12-08 10:30:00'),
-- ('RTG7KW','DANIELLE','GONZALEZ','9095698490','2','100001','DOLLARS','65','Wanna Get Away','2015-12-08 10:30:00'),
-- sudo python sw_flight_search.py SJC ONT 2015-12-26 2015-12-29
('R8AFC6','LORENZO','JAVIER','9252007284','11','100002','POINTS','12918','Wanna Get Away','2015-12-08 10:30:00'),
('R8AFC6','LORENZO','JAVIER','9252007284','11','100003','POINTS','11029','Wanna Get Away','2015-12-08 10:30:00');
-- sudo python sw_flight_search.py SJC MSY 2016-02-06 2016-02-09

INSERT INTO AIRPORTS (AIRPORT_CODE,AIRPORT_CITY,AIRPORT_NAME,AIRPORT_LATITUDE,AIRPORT_LONGITUDE,AIRPORT_TIMEZONE) VALUES
('CAK','Akron-Canton, OH - CAK','Akron Canton Airport','40.9149599','-81.4365916','Eastern Standard Time'),
('ALB','Albany, NY - ALB','Albany International Airport','42.7487124','-73.8054981','Eastern Standard Time'),
('ABQ','Albuquerque, NM - ABQ','Albuquerque International Sunport','35.0433333','-106.6129085','Mountain Standard Time'),
('AMA','Amarillo, TX - AMA','Rick Husband Amarillo International Airport','35.2184869','-101.7052103','Central Standard Time'),
('AUA','Aruba, Aruba - AUA','Queen Beatrix International Airport','12.5015939','-70.0119926','Atlantic Standard Time'),
('ATL','Atlanta, GA - ATL','Hartsfield-Jackson Atlanta International Airport','33.6407282','-84.4277001','Eastern Standard Time'),
('AUS','Austin, TX - AUS','Austin-Bergstrom International Airport','30.1974292','-97.6663058','Central Standard Time'),
('BWI','Baltimore/Washington, MD - BWI','Baltimore/Washington International Thurgood Marshall Airport','39.1774042','-76.6683922','Eastern Standard Time'),
('BZE','Belize City, Belize - BZE','Philip S.W. Goldson International Airport','17.5045661','-88.1962133','Central Standard Time'),
('BHM','Birmingham, AL - BHM','Birmingham-Shuttlesworth International Airport','33.5624269','-86.754126','Central Standard Time'),
('BOI','Boise, ID - BOI','Boise Airport','43.5658231','-116.222316','Mountain Standard Time'),
('BOS','Boston Logan, MA - BOS','Boston Logan International Airport','42.3656132','-71.0095602','Eastern Standard Time'),
('BUF','Buffalo/Niagara, NY - BUF','Buffalo Niagara International Airport','42.9397059','-78.7295067','Eastern Standard Time'),
('BUR','Burbank, CA - BUR','Bob Hope Airport','34.1983122','-118.3574036','Pacific Standard Time'),
('SJD','Cabo San Lucas/Los Cabos, MX - SJD','Los Cabos International Airport','22.8905327','-109.9167371','Mexican Pacific Standard Time'),
('CUN','Cancun, Mexico - CUN','Cancun International Airport','21.0403409','-86.873564','Eastern Standard Time'),
('CHS','Charleston, SC - CHS','Charleston International Airport','32.8942676','-80.038159','Eastern Standard Time'),
('CLT','Charlotte, NC - CLT','Charlotte Douglas International Airport','35.2144026','-80.9473146','Eastern Standard Time'),
('MDW','Chicago (Midway), IL - MDW','Chicago Midway International Airport','41.7867759','-87.7521884','Central Standard Time'),
('CLE','Cleveland, OH - CLE','Cleveland Hopkins International Airport','41.4124339','-81.8479925','Eastern Standard Time'),
('CMH','Columbus, OH - CMH','Port Columbus International Airport','39.9999399','-82.8871767','Eastern Standard Time'),
('CRP','Corpus Christi, TX - CRP','Corpus Christi International Airport','27.7744653','-97.5027118','Central Standard Time'),
('DAL','Dallas (Love Field), TX - DAL','Dallas Love Field Airport','32.8481029','-96.8512063','Central Standard Time'),
('DAY','Dayton, OH - DAY','Dayton International Airport','39.9025242','-84.2217719','Eastern Standard Time'),
('DEN','Denver, CO - DEN','Denver International Airport','39.838854','-104.665877','Mountain Standard Time'),
('DSM','Des Moines, IA - DSM','Des Moines International Airport','41.5341333','-93.6587958','Central Standard Time'),
('DTW','Detroit, MI - DTW','Detroit Metropolitan Wayne County Airport','42.2161722','-83.3553842','Eastern Standard Time'),
('ELP','El Paso, TX - ELP','El Paso International Airport','31.8053354','-106.3824345','Mountain Standard Time'),
('FNT','Flint, MI - FNT','Bishop International Airport','42.9736283','-83.7390224','Eastern Standard Time'),
('FLL','Ft. Lauderdale, FL - FLL','Fort Lauderdale-Hollywood International Airport','26.0742344','-80.1506022','Eastern Standard Time'),
('RSW','Ft. Myers, FL - RSW','Southwest Florida International Airport','26.5337051','-81.7553083','Eastern Standard Time'),
('GRR','Grand Rapids, MI - GRR','Gerald R. Ford International Airport','42.8846633','-85.5248434','Eastern Standard Time'),
('GSP','Greenville/Spartanburg, SC - GSP','Greenville-Spartanburg International Airport','34.8959008','-82.2172338','Eastern Standard Time'),
('HRL','Harlingen, TX - HRL','Valley International Airport','26.1906306','-97.6961026','Central Standard Time'),
('BDL','Hartford, CT - BDL','Bradley International Airport','41.9388735','-72.6860314','Eastern Standard Time'),
('HOU','Houston (Hobby), TX - HOU','William P. Hobby Airport','29.6541074','-95.2766145','Central Standard Time'),
('IND','Indianapolis, IN - IND','Indianapolis International Airport','39.7168593','-86.2955952','Eastern Standard Time'),
('JAX','Jacksonville, FL - JAX','Jacksonville International Airport','30.4940713','-81.6879368','Eastern Standard Time'),
('MCI','Kansas City, MO - MCI','Kansas City International Airport','39.3006427','-94.7125937','Central Standard Time'),
('LAS','Las Vegas, NV - LAS','McCarran International Airport','36.0839998','-115.1537389','Pacific Standard Time'),
('LIR','Liberia, Costa Rica - LIR','Daniel Oduber Quiros International Airport','10.5996226','-85.5383035','Central Standard Time'),
('LIT','Little Rock, AR - LIT','Bill and Hillary Clinton National Airport','34.7307049','-92.2216531','Central Standard Time'),
('ISP','Long Island/Islip, NY - ISP','Long Island MacArthur Airport','40.7898451','-73.097568','Eastern Standard Time'),
('LAX','Los Angeles, CA - LAX','Los Angeles International Airport','33.9415889','-118.40853','Pacific Standard Time'),
('SDF','Louisville, KY - SDF','Louisville International Airport','38.175662','-85.7369231','Eastern Standard Time'),
('LBB','Lubbock, TX - LBB','Preston Smith International Airport','33.6562701','-101.8209749','Central Standard Time'),
('MHT','Manchester, NH - MHT','Manchester-Boston Regional Airport','42.929687','-71.4352177','Eastern Standard Time'),
('MEM','Memphis, TN - MEM','Memphis International Airport','35.0420679','-89.9791729','Central Standard Time'),
('MEX','Mexico City, Mexico - MEX','Mexico City International Airport','19.5362775','-99.0619389','Central Standard Time'),
('MAF','Midland/Odessa, TX - MAF','Midland International Air & Space Port','31.9417386','-102.2047497','Central Standard Time'),
('MKE','Milwaukee, WI - MKE','General Mitchell International Airport','42.9475534','-87.896646','Central Standard Time'),
('MSP','Minneapolis/St. Paul (Terminal 2), MN - MSP','Minneapolis−Saint Paul International Airport','44.8847554','-93.2222846','Central Standard Time'),
('MBJ','Montego Bay, Jamaica - MBJ','Sangster International Airport','18.5022634','-77.9144344','Eastern Standard Time'),
('BNA','Nashville, TN - BNA','Nashville International Airport','36.126317','-86.6773713','Central Standard Time'),
('NAS','Nassau, Bahamas - NAS','Lynden Pindling International Airport','25.0479835','-77.355413','Eastern Standard Time'),
('MSY','New Orleans, LA - MSY','Louis Armstrong New Orleans International Airport','29.9922012','-90.2590112','Central Standard Time'),
('LGA','New York (LaGuardia), NY - LGA','LaGuardia Airport','40.7769271','-73.8739659','Eastern Standard Time'),
('EWR','New York/Newark, NJ - EWR','Newark Liberty International Airport','40.6895314','-74.1744624','Eastern Standard Time'),
('ORF','Norfolk, VA - ORF','Norfolk International Airport','36.8956837','-76.2000161','Eastern Standard Time'),
('OAK','Oakland, CA - OAK','Oakland International Airport','37.7125689','-122.2197428','Pacific Standard Time'),
('OKC','Oklahoma City, OK - OKC','Will Rogers World Airport','35.393056','-97.600556','Central Standard Time'),
('OMA','Omaha, NE - OMA','Eppley Airfield','41.3035025','-95.8849064','Central Standard Time'),
('ONT','Ontario/LA, CA - ONT','LA/Ontario International Airport','34.0559781','-117.598057','Pacific Standard Time'),
('SNA','Orange County/Santa Ana, CA - SNA','John Wayne Airport','33.6761901','-117.8674759','Pacific Standard Time'),
('MCO','Orlando, FL - MCO','Orlando International Airport','28.4311577','-81.308083','Eastern Standard Time'),
('ECP','Panama City Beach, FL - ECP','Northwest Florida Beaches International Airport','30.3529337','-85.7942695','Central Standard Time'),
('PNS','Pensacola, FL - PNS','Pensacola International Airport','30.4738158','-87.1867049','Central Standard Time'),
('PHL','Philadelphia, PA - PHL','Philadelphia International Airport','39.8743959','-75.2424229','Eastern Standard Time'),
('PHX','Phoenix, AZ - PHX','Phoenix Sky Harbor International Airport','33.4372686','-112.0077881','Mountain Standard Time'),
('PIT','Pittsburgh, PA - PIT','Pittsburgh International Airport','40.4957722','-80.2413113','Eastern Standard Time'),
('PWM','Portland, ME - PWM','Portland International Jetport','43.6464785','-70.3096974','Eastern Standard Time'),
('PDX','Portland, OR - PDX','Portland International Airport','45.4936797','-122.7034499','Pacific Standard Time'),
('PVD','Providence, RI - PVD','T. F. Green Airport','41.7245271','-71.4304062','Eastern Standard Time'),
('PVR','Puerto Vallarta, MX - PVR','Licenciado Gustavo Diaz Ordaz International Airport','20.6805184','-105.2523762','Central Standard Time'),
('PUJ','Punta Cana, DR - PUJ','Punta Cana International Airport','18.562998','-68.363617','Atlantic Standard Time'),
('RDU','Raleigh/Durham, NC - RDU','Raleigh-Durham International Airport','35.880079','-78.7879963','Eastern Standard Time'),
('RNO','Reno/Tahoe, NV - RNO','Reno-Tahoe International Airport','39.5296329','-119.8138027','Pacific Standard Time'),
('RIC','Richmond, VA - RIC','Richmond International Airport','37.5065795','-77.3208112','Eastern Standard Time'),
('ROC','Rochester, NY - ROC','Greater Rochester International Airport','43.1225229','-77.6665722','Eastern Standard Time'),
('SMF','Sacramento, CA - SMF','Sacramento International Airport','38.6950854','-121.5900648','Pacific Standard Time'),
('SLC','Salt Lake City, UT - SLC','Salt Lake City International Airport','40.7899404','-111.9790706','Mountain Standard Time'),
('SAT','San Antonio, TX - SAT','San Antonio International Airport','29.5311973','-98.4683484','Central Standard Time'),
('SAN','San Diego, CA - SAN','San Diego International Airport','32.7338006','-117.1933038','Pacific Standard Time'),
('SFO','San Francisco, CA - SFO','San Francisco International Airport','37.6213129','-122.3789554','Pacific Standard Time'),
('SJC','San Jose, CA - SJC','Mineta San Jose International Airport','37.3639472','-121.9289375','Pacific Standard Time'),
('SJO','San Jose, Costa Rica - SJO','Juan Santamaria Airport','9.9280694','-84.0907246','Central Standard Time'),
('SJU','San Juan, PR - SJU','Luis Munoz Marin International Airport','18.439167','-66.001667','Atlantic Standard Time'),
('SEA','Seattle/Tacoma, WA - SEA','Seattle-Tacoma International Airport','47.4502499','-122.3088165','Pacific Standard Time'),
('GEG','Spokane, WA - GEG','Spokane International Airport','47.6217478','-117.534812','Pacific Standard Time'),
('STL','St. Louis, MO - STL','Saint Louis Downtown Heliport','38.6253391','-90.1830842','Central Standard Time'),
('TPA','Tampa, FL - TPA','Tampa International Airport','27.9834776','-82.5370781','Eastern Standard Time'),
('TUS','Tucson, AZ - TUS','Tucson International Airport','32.1145102','-110.9392269','Mountain Standard Time'),
('TUL','Tulsa, OK - TUL','Tulsa International Airport','36.198778','-95.8838659','Central Standard Time'),
('IAD','Washington (Dulles), DC - IAD','Dulles International Airport','38.9526323','-77.44774','Eastern Standard Time'),
('DCA','Washington (Reagan National), DC - DCA','Ronald Reagan Washington National Airport','38.845697','-77.04836','Eastern Standard Time'),
('PBI','West Palm Beach, FL - PBI','Palm Beach International Airport','26.6857475','-80.0928165','Eastern Standard Time'),
('ICT','Wichita, KS - ICT','Wichita Dwight D. Eisenhower National Airport','37.6508529','-97.4286988','Central Standard Time');

/* ********************************** COMMIT ********************************** */

COMMIT WORK;

/* **************************************************************************** */
