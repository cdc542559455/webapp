import boto3
from boto3.dynamodb.conditions import Key, Attr
import itertools

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
			if (
			    len(trans[0]) !=0 and len(trans[1]) !=0 and 
			    len(trans[2]) != 0
			):
				amount = 0.00
				# calculate single transaction amount
				amount = str("%.2f" % (int(trans[0]) * float(trans[2])))
				trans.append(amount)
				add.append(trans)					
		if len(add) != 0:
			item["Details"] = add	
	# upload table	
	table.put_item(Item = item) 	


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
		result['Item Color'] = r['Product Color']
		result['Material'] = r['Material']
		result['Imprint Method'] = r["Imprint Method"]
		result['Imprint Color'] = r["Imprint Color"]
		result['Attached_picture'] = r['Attached_picture']
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

# --------------------------------------------------------------------------------------------------------------------- #	              


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

if __name__ == '__main__':
	print()