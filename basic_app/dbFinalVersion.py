
import boto3
from boto3.dynamodb.conditions import Key, Attr

'''
Pre-requirement:
    1. Create a S3 bucket "orderpictures"
    2. Create "Invoice", "Order" and "Proof" tables on Oregon (uw-west-2) server
'''

key = "AKIAJZPCRO4GVYOL3SJQ"
secret = "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"
region = "us-west-2"
BUCKET_NAME = "orderpictures"


def generateOrUpdateInvoice(invoiceNumber, invoiceDate, PO, billTo, shipTo, dueDate, cusName, *details):
        # load "Invoice" table
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key, aws_secret_access_key=secret,region_name=region)
        table = dynamodb.Table('Invoice')

        # add necessary info for invoice
        item = {}
        item["Invoice #"] = invoiceNumber
        item["Invoice Date"] = invoiceDate
        item["P.O.#"] = PO
        item["Bill To"] = billTo
        item["Ship To"] = shipTo
        item["Due Date"] = dueDate
        item["Customer Name"] = cusName

        # if there is any transaction details
        if len(details) != 0:
                additem = []
                # calculate each transaction amount and put in additem dir
                for trans in details:
                        amount = 0.00
                        # calculate single transaction amount
                        amount = str("%.2f" % (int(trans[0]) * float(trans[2])))
                        trans.append(amount)
                        additem.append(trans)
                item["Details"] = additem

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
                return None, None


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
                for r in response['Items']:
                        print(print("Order Number: " + str(r["Order Number"])))
                        for k, v in r.items() :
                                if k != "Order Number":
                                        print (k + ": " + v + '\n') 
        else:
                print("No result found")    


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
        
        # print('----------------------------------------------')
        
        # customerQueryProof("100")
        # print('----------------------------------------------')
        # customerQueryInvoice("666")
        x,y = customerQueryInvoice("666")
        print(x)
        print(y)
        print("hello word")
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
        