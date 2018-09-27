#!/usr/bin/python3
from urllib.request import urlopen, Request
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring
from bs4 import BeautifulSoup
from dateutil.parser import parse

o2c = {'UPS Next Day Air Early':'14', 'UPS Next Day Air':'01',
	   'UPS Next Day Air Saver':'13', 'UPS 2nd Day Air AM':'59',
	   'UPS 2nd Day Air':'02', 'UPS 3 Day Select':'12', 'UPS Ground':'03',
	   'UPS Standard':'11', 'UPS Worldwide Express':'07', 'UPS Worldwide Express Plus':'54',
	   'UPS Worldwide Expedited':'08', 'UPS Express Saver':'65', 'UPS Worldwide Saver':'28'}

licenseNum = 'your license number'
userId = 'your user id'
password = 'your password'
version ="""<?xml version="1.0"?>""" 

shipperCity = None
shipperState = 'WA'
shipperZip = '98105'
shipperCountry = 'US'
isShipperResident = False
fromCity = None
fromState = None
fromZip = '610000'
fromCountry = 'CN'
isFromResident = False
toCity = 'NEW YORK'
toState = 'NY'
toZip = '10001'
toCountry = 'US'
isToResident = True
length = '1'
width = '2'
height = '3'
weight = '10'
pickUpDate = '20181001'
numOfPkgs = 1
deliveryDate = '20181015'

def setVal(post, key, assigner):
	if post[key] != '':
		assigner = post[key]

def initializeParas(post):
	li = [['fc', fromCity],['fs', fromState],['fz', fromZip],['fco', fromCountry],
	      ['ifr', isFromResident],['tc', toCity],['ts', toState],['tz', toZip],
	      ['tco', toCountry],['itr', isToResident],['le', length],['wd', width],
	      ['he', height],['pcd', pickUpDate],['dd', deliveryDate],['we', weight]]
	for l in li:
		setVal(post, l[0], l[1])
	if post['nop'] != '':
		numOfPkgs = int(post['nop'])

def addAddress(root, city, state, zipCode, country, isResidential):
	address = SubElement(root,'Address')
	if city != None:
		c = SubElement(address,'City')
		c.text = city
	if state != None:
		s = SubElement(address,'StateProvinceCode')
		s.text = state
	z = SubElement(address,'PostalCode')
	z.text = zipCode
	cou = SubElement(address,'CountryCode')
	cou.text = country
	if isResidential:
		residentChild = SubElement(address,'ResidentialAddressIndicator')
		residentChild.text = ' '

def makeAccessXML(licenseNum, userId, password):
	r = Element('AccessRequest')
	r.set('xml:lang', 'en-US')
	acn = SubElement(r, 'AccessLicenseNumber')
	acn.text = licenseNum
	uid = SubElement(r, 'UserId')
	uid.text = userId
	ps = SubElement(r, 'Password')
	ps.text = password
	return tostring(r).decode("utf-8") 

def makeRateRequestXML(code, isSatDelivered):
	r = Element('RatingServiceSelectionRequest')
	r.set('xml:lang', 'en-US')

	req = SubElement(r, 'Request')
	tr = SubElement(req, 'TransactionReference')
	cc = SubElement(tr, 'CustomerContext')
	cc.text = 'Rating and Service'
	xc = SubElement(tr, 'XpciVersion')
	xc.text = '1.0'
	ra = SubElement(req, 'RequestAction')
	ra.text = 'Rate'
	ro = SubElement(req, 'RequestOption')
	ro.text = 'Rate'

	pt = SubElement(r, 'PickupType')
	co = SubElement(pt, 'Code')
	co.text = '07'

	shipment = SubElement(r, 'Shipment')
	shipper = SubElement(shipment, 'Shipper')
	addAddress(shipper, shipperCity, shipperState, shipperZip, shipperCountry, isShipperResident)
	if isSatDelivered:
		sso = SubElement(shipment, 'ShipmentServiceOptions')
		sat = SubElement(sso, 'SaturdayDelivery')
		sat.text = ' '

	to = SubElement(shipment, 'ShipTo')
	addAddress(to, toCity, toState, toZip, toCountry, isToResident)
	shipFrom = SubElement(shipment, 'ShipFrom')
	addAddress(shipFrom, fromCity, fromState, fromZip, fromCountry, isFromResident)

	serv = SubElement(shipment, 'Service')
	co1 = SubElement(serv, 'Code')
	co1.text = code

	for i in range(numOfPkgs):
		pck = SubElement(shipment, 'Package')
		tp = SubElement(pck, 'PackagingType')
		co2 = SubElement(tp, 'Code')
		co2.text = '02'
		dms = SubElement(pck, 'Dimensions')
		meas = SubElement(dms, 'UnitOfMeasurement')
		co3 = SubElement(meas, 'Code')
		if fromCountry == 'CN':
			co3.text = 'CM'
		else:
			co3.text = 'IN'
		le = SubElement(dms, 'Length')
		le.text = length
		wid = SubElement(dms, 'Width')
		wid.text = width
		hi = SubElement(dms, 'Height')
		hi.text = height

		pckWei = SubElement(pck, 'PackageWeight')
		meas1 = SubElement(pckWei, 'UnitOfMeasurement')
		co4 = SubElement(meas1, 'Code')
		if fromCountry == 'CN':
			co4.text = 'KGS'
		else:
			co4.text = 'LBS'
		wei = SubElement(pckWei, 'Weight')
		wei.text = weight

	return version+makeAccessXML(licenseNum,userId,password)+version+tostring(r).decode("utf-8") 



def addAddress2Transit(root, city, state, zipCode, country, isResidential):
	addreFormat = SubElement(root, 'AddressArtifactFormat')
	if city != None:
		c = SubElement(addreFormat, 'PoliticalDivision2')
		c.text = city
	if state != None:
		s = SubElement(addreFormat, 'PoliticalDivision1')
		s.text = state
	z = SubElement(addreFormat, 'PostcodePrimaryLow')
	z.text = zipCode
	con = SubElement(addreFormat, 'CountryCode')
	con.text = country
	if isResidential:
		resdi = SubElement(addreFormat, 'ResidentialAddressIndicator')
		resdi.text = ' '


def makeTimeRequestXml():
	r = Element('TimeInTransitRequest')
	r.set('xml:lang', 'en-US')

	req = SubElement(r, 'Request')
	tr = SubElement(req, 'TransactionReference')
	xc = SubElement(tr, 'XpciVersion')
	xc.text = '1.001'
	ra = SubElement(req, 'RequestAction')
	ra.text = 'TimeInTransit'
	
	traFrom = SubElement(r, 'TransitFrom')
	addAddress2Transit(traFrom, fromCity, fromState, fromZip, fromCountry, isFromResident)
	traTo = SubElement(r, 'TransitTo')
	addAddress2Transit(traTo, toCity, toState, toZip, toCountry, isToResident)

	pkDate = SubElement(r, 'PickupDate')
	pkDate.text = pickUpDate
	maxSize = SubElement(r, 'MaximumListSize')
	maxSize.text = '35'

	invoice = SubElement(r, 'InvoiceLineTotal')
	currency = SubElement(invoice, 'CurrencyCode')
	if fromCountry == 'CN':
		currency.text = 'RMB'
	else:
		currency.text = 'USD'
	mv = SubElement(invoice, 'MonetaryValue')
	mv.text = '50'

	sw = SubElement(r, 'ShipmentWeight')
	unit = SubElement(sw, 'UnitOfMeasurement')
	co = SubElement(unit, 'Code')
	if fromCountry == 'CN':
		co.text = 'KGS'
	else:
		co.text = 'LBS'	
	wei = SubElement(sw, 'Weight')
	wei.text = weight

	return version+makeAccessXML(licenseNum,userId,password)+version+tostring(r).decode("utf-8") 

def getOptionWithTime(): 
	data = makeTimeRequestXml()
	#print(data)	
	httpresq = Request(url="https://onlinetools.ups.com/ups.app/xml/TimeInTransit", data=data.encode('utf_8'), headers={'Content-Type': 'application/x-www-form-urlencoded'})
	response = urlopen(httpresq)
	return_values = response.read()
	#print(return_values)
	r = fromstring(return_values)
	li = []    # list of [des, isSatDelivered, btds, hdc, deldate, time, dow, totalDays]
	if r.find('Response').find('ResponseStatusCode').text == '0': 
		print(r.find('Response').find('Error').find('ErrorDescription').text) 
	elif r.find('TransitResponse') == None:
		print('No options for current origin to destination')
	else:
		for ss in r.find('TransitResponse').findall('ServiceSummary'):
		  ser = ss.find('Service')
		  des = ser.find('Description').text # des
		  isSatDelivered = False
		  arr = ss.find('EstimatedArrival') 
		  btds = arr.find('BusinessTransitDays').text 
		  hdc = None
		  if arr.find('HolidayCount')!= None:
		  	hdc = arr.find('HolidayCount').text
		  deldate = arr.find('Date').text  # scheduled delivery date
		  time = arr.find('Time').text # scheduled delivery time
		  dow = arr.find('DayOfWeek').text 
		  totalDays = None
		  if arr.find('TotalTransitDays')!= None:
		  	totalDays = arr.find('TotalTransitDays').text
		  if ss.find('SaturdayDelivery') != None and ss.find('SaturdayDelivery').text == '1':
		  	isSatDelivered = True
		  li.append([des, isSatDelivered, btds, hdc, deldate, time, dow, totalDays])
	return li


def makeServiceWithPrice(optionList):
	#print(optionList)

	for i in range(len(optionList)-1, -1, -1):
		#print(opt[0])
		if optionList[i][0] in o2c:			
			xml = makeRateRequestXML(o2c[optionList[i][0]], optionList[i][1]).encode('utf_8')
			httpresq = Request(url="https://onlinetools.ups.com/ups.app/xml/Rate", data=xml, headers={'Content-Type': 'application/x-www-form-urlencoded'})
			response = urlopen(httpresq)
			return_values = response.read()
			#print(return_values)
			#print('hello2')
			y=BeautifulSoup(return_values,'html.parser').ratingserviceselectionresponse
			if y != None and y.response.responsestatuscode.string=='0':
				#print(y.response.error.errordescription.string)
				#print('hello3')
				continue

			#print('hello')
			r = fromstring(return_values)
			#print(r.find('Response').find('ResponseStatusDescription').text)
			#print(m[opt], r.find('RatedShipment').find('RatedPackage').find('TotalCharges').find('MonetaryValue').text)
			charge = r.find('RatedShipment').find('TotalCharges').find('MonetaryValue').text
			if fromCountry == 'US' and toCountry == 'US':
				charge = r.find('RatedShipment').find('TransportationCharges').find('MonetaryValue').text
			optionList[i].append(charge)
			currency = r.find('RatedShipment').find('TotalCharges').find('CurrencyCode').text
			optionList[i].append(currency)
		else:
			del optionList[i]


def getMinOption(optionList):
	onTime = False	
	beforeList = []
	minPrice = 99999999.0
	afterList = []
	#print('intialized afterList:',afterList)
	minDateDiff = -100
	expectDate = parse(deliveryDate)
	for opt in optionList:
		actualDate = parse(opt[4])
		diffStr = str(expectDate - actualDate).split(' ')[0]
		#print(diffStr)
		diff = 0
		if diffStr != '0:00:00':
			diff = int(diffStr)
		if diff >= 0 and diff <= 3:
			onTime = True
			if float(opt[8]) < minPrice:
				minPrice = float(opt[8])
			beforeList.append(opt)
		if (diff < 0) and (not onTime):
			if diff > minDateDiff:
				minDateDiff = diff
			temp = [item for item in opt]
			temp.append(diff)
			afterList.append(temp)

	if len(beforeList) == 0 and len(afterList) == 0:
		return [['No option for this pickUpDate and deliveyDate']]

	if onTime:
		for i in range(len(beforeList)-1, -1, -1):
			if float(beforeList[i][8]) > minPrice:
				del beforeList[i]
		return beforeList[0]
	else:
		for j in range(len(afterList)-1, -1, -1):
			if float(afterList[j][10]) < minDateDiff:
				del afterList[j]
		return afterList[0]


