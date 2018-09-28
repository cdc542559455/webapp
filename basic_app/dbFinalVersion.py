
import boto3
from boto3.dynamodb.conditions import Key, Attr
import itertools

'''
Pre-requirement:
    1. Create a S3 bucket "orderpictures"
    2. Create "Invoice", "Order" and "Proof" tables on Oregon (uw-west-2) server
'''

key = "AKIAJZPCRO4GVYOL3SJQ"
secret = "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"
region = "us-west-2"
BUCKET_NAME = "orderpictures"

def generateOrUpdateInvoice(info, additional):
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
	table = dynamodb.Table('Invoice')

	# add necessary info for invoice
	item = {}
	item["Invoice #"] = info[0]
	item["Invoice Date"] = info[1]
	item["P.O.#"] = info[2]
	item["Bill To"] = info[3]
	item["Ship To"] = info[4]
	item["Due Date"] = info[5]
	item["Customer Name"] = info[6]

	# if there is any transaction details
	if len(additional) != 0:
		add = []
		for trans in additional:
			amount = 0.00
			# calculate single transaction amount
			amount = str("%.2f" % (int(trans[0]) * float(trans[2])))
			trans.append(amount)
			add.append(trans)
		item["Details"] = add
			
	# upload table	
	table.put_item(Item = item) 	


def customerQueryInvoice(invoiceNumber):
        # load "Invoice" table
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Invoice')

        response = table.query(
                KeyConditionExpression=Key('Invoice #').eq(invoiceNumber)
        )

        # total Amount
        total = 0.00

        if not len(response['Items']) == 0:
                x = response['Items'][0]
                y = response['Items'][0]['Details']
                x.pop('Details', None)
                for price in y:
                        total += float(price[3])
                return x, y, total
        else:
                return None, None, None
                
def uploadToS3(path):
	try:
		open(path, 'r')
	except OSError:
		print("cant find: " + path)
		return
	fileName = path.split("\\")[len(path.split("\\")) - 1]
	user = boto3.client(service_name='s3', aws_access_key_id = key, aws_secret_access_key = secret)
	s3 = boto3.resource('s3')

	MyS3Objects = [s.key for s in s3.Bucket(BUCKET_NAME).objects.filter(Prefix="")]
	if fileName in MyS3Objects:
		print(fileName, " is already on S3")
		return

	transfer = boto3.s3.transfer.S3Transfer(user)
	transfer.upload_file(path, BUCKET_NAME, fileName)
	object_acl = s3.ObjectAcl(BUCKET_NAME,fileName)
	response = object_acl.put(ACL='public-read')
	url = "https://s3-us-west-2.amazonaws.com/orderpictures/" + fileName
	return (url)


def creatProof(PO, cusName, itemNum, quantity, material, size, item_color, imprint_method, imprint_color, picture_path):
        # load "Proof" table
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Proof')

        # get feedback URL for order picture
        pictureUrl = uploadToS3(picture_path)

        item = {}
        item["PO Number"] = PO
        item["Customer Name"] = cusName
        item["Item Number"] = itemNum
        item["Quantity"] = quantity
        item["Material"] = material
        item["Size / Capacity"] = size
        item["Item Color"] = item_color
        item["Imprint Method"] = imprint_method
        item["Imprint Color"] = imprint_color
        item["Attached_picture"] = pictureUrl

        # upload table
        table.put_item(Item = item)


def generateOrUpdateOrder(orderNumber, orderDate, inHandDate, shippingMethod, deliverAddr, nexusIdentityItemNum, size,
                     material, quantity, productColor, imprintMethod, imprintColor, cusName, PO, picture_path, **add):
        # load "Order" table
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        orderTable = dynamodb.Table('Order')

        orderItem = {}
        orderItem["Order Number"] = orderNumber
        orderItem["Order Date"] = orderDate
        orderItem["In-Hands Date (in USA)"] = inHandDate
        orderItem["Shipping Method"] = shippingMethod
        orderItem["Delivery Address"] = deliverAddr
        orderItem["Nexus Identity Item Number"] = nexusIdentityItemNum
        orderItem["Quantity"] = quantity
        orderItem["Product Color"] = productColor
        orderItem["Size"] = size
        orderItem["Material"] = material
        orderItem["Imprint Method"] = imprintMethod
        orderItem["Imprint Color"] = imprintColor
        orderItem["Customer Name"] = cusName

        if (len(add) != 0):
                for k, v in add.items():
                        orderItem[k] = v

        # upload order table
        orderTable.put_item(Item = orderItem)

        # meanwhile update the proof table
        creatProof(PO, cusName, nexusIdentityItemNum, quantity, material, size, productColor, imprintMethod, imprintColor, picture_path)



def customerQueryOrder(orderNumber):
        # load "Order" table
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Order')
        response = table.query(
                KeyConditionExpression=Key('Order Number').eq(orderNumber)
        )

        if not len(response['Items']) == 0:
                return response['Items'][0]
        else:
                return None


def customerQueryProof(PO):
        # load "Order" table
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Proof')
        response = table.query(
                KeyConditionExpression=Key('PO Number').eq(PO)
        )

        if not len(response['Items']) == 0:
                return response['Items'][0]
        else:
                return None


def employeeScanInvoice():
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Invoice')
        if not len(table.scan()['Items']) == 0:
                for r in table.scan()['Items']:
                        customerQueryInvoice(r['Invoice #'])
                        print('-----------------------------------------------------')


def employeeScanProof():
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Proof')
        if not len(table.scan()['Items']) == 0:
                for r in table.scan()['Items']:
                        for k, v in r.items() :
                                print (k + ": " + str(v))
                        print()

def employeeScanOrder():
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Order')
        if not len(table.scan()['Items']) == 0:
                for r in table.scan()['Items']:
                        for k, v in r.items() :
                                print (k + ": " + str(v))
                        print()

def queryProof(PONumber):
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
	table = dynamodb.Table('Order')     
	response = table.scan(
	    FilterExpression=Attr('PO Number').eq(PONumber)
	)
	result = {}
	if not len(response['Items']) == 0:
		r = response['Items'][0]
		result['PO Number']	= r['PO Number']
		result['Customer Name'] = r["Customer Name"]
		result['Item Number'] = r['Nexus Identity Item Number']
		result['Quantity'] = r['Quantity']
		result['Size/Capacity'] = r['Size']
		result['Item Color'] = r['Product Color']
		result['Material'] = r['Material']
		result['Imprint Method'] = r["Imprint Method"]
		result['Imprint Color'] = r["Imprint Color"]
		result['Attached_picture'] = r['Attached_picture']
	return result

def partialEmployeeScanInvoice():
    # load "Invoice" table
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
    table = dynamodb.Table('Invoice')
    result = []
    if not len(table.scan()['Items']) == 0:
        for r in table.scan()['Items']:
            # total Amount
            total = 0.00
            oneInvoice = []
            if (len(r["Details"]) != 0):
                for l in r["Details"]:
                    total += float(l[3])
            oneInvoice.append(r["Invoice #"])
            oneInvoice.append(r["Invoice Date"])
            oneInvoice.append(str("%.2f" % total))
            result.append(oneInvoice)
    else:
            pass
    return result

def partialScanProof():
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
	table = dynamodb.Table('Order')
	result = []
	if not len(table.scan()['Items']) == 0:
		for r in table.scan()['Items']:
			sr = []
			sr.append(r['PO Number']) 
			sr.append(r['Nexus Identity Item Number'])
			sr.append(r['Quantity'])
			result.append(sr)
	return result

def showFullOrder(orderNumber):
	# load "Order" table
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
	table = dynamodb.Table('Order')
	response = table.query(
	    KeyConditionExpression=Key('Order Number').eq(orderNumber)
	)
	resultList = []
	addtionDirct = {}
	if not len(response['Items']) == 0:
		r = response['Items'][0]
		resultList.append(str(r['Order Number']))
		resultList.append(str(r['Order Date']))
		resultList.append(str(r['In-Hands Date (in USA)']))
		resultList.append(str(r['Shipping Method']))
		resultList.append(str(r['Delivery Address']))
		resultList.append(str(r['Nexus Identity Item Number']))
		resultList.append(str(r["Material"]))
		resultList.append(str(r["Quantity"]))
		resultList.append(str(r["Product Color"]))
		resultList.append(str(r["Imprint Method"]))
		resultList.append(str(r["Imprint Color"]))
		resultList.append(str(r["Customer Name"]))
		resultList.append(str(r["PO Number"]))
		resultList.append(str(r["Attached_picture"]))

		# fill addtionDirct with additional parameter
		addtionDirct = r
		addtionDirct.pop('Order Number')
		addtionDirct.pop('Order Date')
		addtionDirct.pop('In-Hands Date (in USA)')
		addtionDirct.pop('Shipping Method')
		addtionDirct.pop('Delivery Address')
		addtionDirct.pop('Nexus Identity Item Number')
		addtionDirct.pop("Material")
		addtionDirct.pop("Quantity")
		addtionDirct.pop("Product Color")
		addtionDirct.pop("Imprint Method")
		addtionDirct.pop("Imprint Color")
		addtionDirct.pop("Customer Name")
		addtionDirct.pop("PO Number")
		addtionDirct.pop("Attached_picture")
	return resultList, addtionDirct

def deleteItem(tableName, primaryKey):
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
	table = dynamodb.Table(tableName)
	k = {}
	if tableName is "Invoice":
		k["Invoice #"] = str(primaryKey)
	elif tableName is "Order":
		k["Order Number"] = str(primaryKey) 
	else:
		return
	table.delete_item(Key = k)


def partialEmployeeScanOrder():
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
    table = dynamodb.Table('Order')
    result = []
    if not len(table.scan()['Items']) == 0:
        for r in table.scan()['Items']:
                oneOrder = []
                oneOrder.append(str(r['Order Number']))
                oneOrder.append(str(r['Customer Name']))
                oneOrder.append(str(r['Delivery Address']))
                result.append(oneOrder)
    return result

def ChinaEmployeeUpdatePicture(orderID, path):
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
	table = dynamodb.Table('Order')
	Keys = {}
	Keys["Order Number"] = str(orderID)
	table.update_item(
	    Key = Keys,
	    UpdateExpression='SET Attached_picture = :val1',
	    ExpressionAttributeValues={
	            ':val1': path
	    }
	)

def queryProof(PONumber):
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
	table = dynamodb.Table('Order')     
	response = table.scan(
	    FilterExpression=Attr('PO Number').eq(PONumber)
	)
	result = {}
	if not len(response['Items']) == 0:
		r = response['Items'][0]
		result['PO Number']	= r['PO Number']
		result['Customer Name'] = r["Customer Name"]
		result['Item Number'] = r['Nexus Identity Item Number']
		result['Quantity'] = r['Quantity']
		result['Size/Capacity'] = r['Size']
		result['Item Color'] = r['Product Color']
		result['Material'] = r['Material']
		result['Imprint Method'] = r["Imprint Method"]
		result['Imprint Color'] = r["Imprint Color"]
		result['Attached_picture'] = r['Attached_picture']
	return result

def employeeQueryInvoice(invoiceNumber):
	# load "Invoice" table
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Invoice')

        response = table.query(
                KeyConditionExpression=Key('Invoice #').eq(invoiceNumber)
        )   
	
        result = []
        result2 = []
        if not len(response['Items']) == 0:
                r = response['Items'][0]
                result.append(r["Invoice #"])
                result.append(r['Invoice Date'])
                result.append(r['P.O.#'])
                result.append(r['Bill To'])
                result.append(r['Ship To'])
                result.append(r['Due Date'])
                result.append(r['Customer Name'])
                for detail in r['Details']:
                        result2.append(detail[:3])
        return result, result2
	

def generateOrUpdateOrderAndProof(info):
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
	orderTable = dynamodb.Table('Order')

	orderItem = {}
	orderItem["Order Number"] = info[0]
	orderItem["Order Date"] = info[1]
	orderItem["In-Hands Date (in USA)"] = info[2]
	orderItem["Shipping Method"] = info[3]
	orderItem["Delivery Address"] = info[4]
	orderItem["Nexus Identity Item Number"] = info[5]
	orderItem["Material"] = info[6]
	orderItem["Quantity"] = info[7]
	orderItem["Imprint Color"] = info[8]
	orderItem["Imprint Method"] = info[9]
	orderItem["Product Color"] = info[10]
	orderItem["Customer Name"] = info[11]
	orderItem["PO Number"] = info[12]
	orderItem["Attached_picture"] = str(uploadToS3(info[13]))
	add = info[14]
	if (len(add) != 0):
		for k, v in add.items():
			orderItem[k] = v
	#print(orderItem)
	# upload order table
	orderTable.put_item(Item = orderItem)

def partialEmployeeScanProof():
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
    table = dynamodb.Table('Proof')     
    result = []
    if not len(table.scan()['Items']) == 0:
        for r in table.scan()['Items']:
            oneProof = []
            oneProof.append(str(r['PO Number']))
            oneProof.append(str(r['Item Number']))
            oneProof.append(str(r['Quantity']))
            result.append(oneProof)
            print("PO Number: " + str(r['PO Number']))
            print("Item Number: " + str(r['Item Number']))
            print("Quantity: " + str(r['Quantity']))
            print()      
    print(result)
    return result
'''
Fake order:
1. Order#: 555, orderDate: 9-24-2018, inHandDate: 9-28-2018, shippingMethod: AIR, deliverAddr: 8010 NE, nexusIdentityItemNum: 1
   size: 10oz, material: wood, quantity: 10, productColor: red, imprintMethod: wtf, imprintColor: blue, cusName: Hongfei Xie
   PO: 100, picture_path: C:\\Users\\dazha\\Desktop\\New folder\\2.jpg,            add1 = "NO THANKS", add2 = "NO MORE"

2. Order#: 333, orderDate: 2018, inHandDate: 2019, shippingMethod: Ground, deliverAddr: 23120 NE, nexusIdentityItemNum: 0
   size: 100oz, material: steel, quantity: 30, productColor: black, imprintMethod: OMG, imprintColor: white, cusName: Loki
   PO: 200, picture_path: C:\\Users\\dazha\\Desktop\\New folder\\1.jpg,            addtionalInfo = "CHECK ONLY"
'''
if __name__ == '__main__':
        # generateOrUpdateOrder("458", "9-24-2018", "9-28-2018", "AIR", "8010 NE", "1", "10oz", "wood", "10", "red", "wtf", "blue",
        #                  "Hongfei Xie", "100",  "C:\\Users\\lokic\\OneDrive\\desktop\\Actual_Project\\webapp\\media\basic_app\\mainImage\\account-bank-banking-862730.jpg",
        #                  add1 = "NO THANKS", add2 = "NO MORE")
        #   generateOrUpdateOrder
        # print('----------------------------------------------')

        # customerQueryProof("100")
        # print('----------------------------------------------')
        # customerQueryInvoice("666")
        # x,y = customerQueryInvoice("666")
        # print(x)
        # print(y)
        # partialEmployeeScanOrder()
        # print("hello word")
        # l = ["a", "b", "c", "d", "e"]
        # print(l)
        # d = dict(itertools.zip_longest(*[iter(l)] * 2, fillvalue=""))
        # print(d)
        # customerQueryProof("100")
        # print('----------------------------------------------')

        # generateOrUpdateInvoice("4295","09/14/2018","05-215061-B","me","you", "09/14/2018",
        #                    "Alex", ["500", "OMG", "1"], ["302", "SWS1", "0.85"], ["302", "PP", "0.17"], ["1", "SS", "50"])

        # generateOrUpdateInvoice("666","14/2018","2-B","hello","where are you", "1/2018",
        #                    "Iris", ["10", "fk", "3"], ["2", "fish", "7.85"])
        # print('----------------------------------------------')

        # print('***************************************')
        # employeeScanOrder()
        # print('***************************************')
        # employeeScanProof()
        # print('***************************************')
        # employeeScanInvoice()
        # print('***************************************')
        # x, y = showFullOrder('555')
        # print(x)
        # print(y)
        # l = list(range(5,10))
        # print(l)
        # generateOrUpdateOrderAndProof(["333333sss", "9-24-2018", "9-28-2018", "AIR", "230120 8th AVE SE", "IBN-300", "10oz", "wood", "100", "red", "wtf", "blue",
	#                       "Alex Xie", "100", "C:\\Users\\lokic\\OneDrive\\desktop\\Actual_Project\\webapp\\googluck.jpg", { "tryAdd":"YES", "tryAdd2":"WORKED"}])
       x,y = employeeQueryInvoice('666')
       print(x)
       print(y)
       print(len(y))
