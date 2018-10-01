import itertools
from unipath import Path
from django.shortcuts import render, get_object_or_404, redirect, render
from .forms import StaffSignUpForm
from django.utils.decorators import method_decorator
from .decorators import customer_required, staffInChina_required, staffInUSA_required, supervisor_required, supervisor_or_staffInUSA_required
# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm

from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, ListView, UpdateView, TemplateView
from .dbFinalVersion import partialEmployeeScanOrder, customerQueryOrder, showFullOrder, ChinaEmployeeUpdatePicture, generateOrUpdateOrderAndProof,\
partialScanProof, queryProof, partialEmployeeScanInvoice, generateOrUpdateInvoice, employeeQueryInvoice, deleteItem, customerQueryInvoice, chinaQuery, ChinaEmployeeUpdatePicture
import itertools
from django.contrib.staticfiles import finders

from .upsBackEnd import getOptionWithTime, makeServiceWithPrice, getMinOption
from dateutil.parser import parse
from datetime import datetime
from dateutil.tz import tzlocal
# Create your views here.
def home(request):
    return render(request,'basic_app/home.html')

class SignUp(generic.CreateView):
    form_class = StaffSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'basic_app/registration.html'


def user_login(request):

    return render(request,'registration/login.html')


@login_required
@customer_required
def CustomerProofSearch(request):
    pic_src = None
    dic = None
    hasPost = False
    if request.method == 'POST':
        value = str(request.POST.get('orderNumber'))
        hasPost = True
        dic = queryProof(value)
        if (dic):
            pic_src = dic['Attached_picture']
            dic = dict(itertools.islice(dic.items(),1, len(dic)))
    else:
        pass
    return render(request, 'basic_app/customer_proof_search.html',{'hasPost': hasPost, 'dic':dic, 'pic_src':pic_src} )


@login_required
@customer_required
def CustomerInvoiceSearch(request):
    dic = None
    list1 = None
    totalamout = 0
    hasPost = False
    if request.method == 'POST':
        value = str(request.POST.get('invoiceNumber'))
        dic, list1, totalamout = customerQueryInvoice(value)
        hasPost = True
    else:
        pass
    return render(request, 'basic_app/customer_invoice_search.html', {'hasPost': hasPost, 'dic':dic, 'list1': list1, 'totalamout': totalamout} )

@login_required
@supervisor_or_staffInUSA_required
def CustomerInUSAOrderPage(request):
    list_all_order = None
    if request.method == 'POST':
        # to add new row order
        orderNumber = request.POST.get('orderID')
        deleteItem('Order',orderNumber)
        return redirect(reverse('basic_app:StaffInUSAMangement'))
    else:
        list_all_order = partialEmployeeScanOrder()
    return render(request, 'basic_app/staff_in_usa_order_page.html', {'list_all_order':list_all_order })

@login_required
@supervisor_or_staffInUSA_required
def OrderCreatePage(request):
    listpart = None
    newCompound = None
    pic_src = None
    if request.method == 'POST':
        orderID = request.POST.get('orderID', '-1')
        input = request.POST.dict()
        del input['csrfmiddlewaretoken']
        if(orderID == '-1'):
            listInput = list(input.values())
            fistpart = listInput[:14]
            secondpart = listInput[14:]
            kk = dict(itertools.zip_longest(*[iter(secondpart)]*2, fillvalue=""))
            fistpart.append(kk)
            generateOrUpdateOrderAndProof(fistpart)
            return redirect(reverse('basic_app:StaffInUSAMangement'))


        else:
            listpart,dictpart = showFullOrder(orderID)
            pic_src = listpart[13]
            extraRow = len(dictpart)
            namelist = list(range(15,15+2*extraRow+1))
            namelist = namelist[::2]
            container = []
            for key, value in dictpart.items():
                temp = [key, value]
                container.append(temp)
            newCompound = dict(zip(namelist,container))        
    else:
        pass
    return render(request, 'basic_app/order_create.html', {'listpart':listpart, 'newCompound': newCompound, 'pic_src':pic_src })

@login_required
@supervisor_or_staffInUSA_required
def CreateInvoice(request):
    firstpart = None
    secondpart = None
    result = ""
    invoiceNumber = request.POST.get('invoiceNumber', '-1')
    idx = '-1'
    idx = request.POST.get('idx', '-1')
    if request.method == 'POST':
        input = request.POST.dict()
        del input['csrfmiddlewaretoken']
        if (invoiceNumber == '-1'):
            weight = request.POST.get('wd', '-1')
            if (weight != '-1'):
                if request.POST['tco'] == 'CN':
                    result = 'Not available for delivery to China'
                elif parse(request.POST['pcd']) >= parse(request.POST['dd']):
                    result = 'Delivery date cannot be the same or earlier than pickup date'
                elif request.POST['fc'] != '' and request.POST['tc'] != '' and request.POST['fc'].upper() == request.POST['tc'].upper():
                    result = 'Delivery to same city is not supported'
                elif request.POST['fz'] == request.POST['tz']:
                    result = 'Delivery to same zipCode is not supported'
                elif parse(str(datetime.now(tzlocal())).split(' ')[0]) == parse(request.POST['pcd']): # time to be handled
                    result = 'Pickup date cannot be current date'
                else:
                    li = getOptionWithTime(request.POST)
                    if li:
                        print('before li:', li)
                        li = makeServiceWithPrice(li, request.POST)
                        print('li in view: ', li)
                        res = getMinOption(li, request.POST)
                        if len(res) == 1:
                            result = res[0]
                        if len(res) > 1:
                            result = res[0]+', deliveried by '+res[4]+' at '+res[5]+' with '+res[8]+' '+res[9]
                        if (idx != '-1' and idx):
                            firstpart,secondpart = employeeQueryInvoice(idx)
                            if ( firstpart and secondpart) :
                                namelist = list(range(8,8+3*len(secondpart)))
                                namelist = namelist[::3]
                                secondpart = dict(zip(namelist,secondpart))
            else:
                inputlist = list(input.values())
                firstpart = inputlist[:7]
                secondpart = inputlist[7:]
                listnestlist = []
                for x in range(len(secondpart)//3):
                    temp = secondpart[3*x:3*x+3]
                    listnestlist.append(temp)
                generateOrUpdateInvoice(firstpart, listnestlist)
                return redirect(reverse('basic_app:StaffInUSAInvoicemangement'))
                
        else:
            firstpart,secondpart = employeeQueryInvoice(invoiceNumber)
            namelist = list(range(8,8+3*len(secondpart)))
            namelist = namelist[::3]
            secondpart = dict(zip(namelist,secondpart))
    else:
        pass
    return render(request, 'basic_app/staff_in_usa_create_invoice.html', {'result':result, 'firstpart':firstpart, 'secondpart':secondpart})

@login_required
@supervisor_or_staffInUSA_required
def invoiceCreatePage(request):
    listofInvoices = None
    if request.method == "POST":
        invoiceNumber = request.POST.get('invoiceNumber')
        deleteItem('Invoice', invoiceNumber)
        return redirect(reverse('basic_app:StaffInUSAInvoicemangement'))

        
    else:
        listofInvoices = partialEmployeeScanInvoice()    
    return render(request, 'basic_app/staff_in_USA_invoice_manage.html', {'listofInvoices':listofInvoices})

@login_required
@staffInChina_required
def StaffInChinaManagement(request):
    list_all_order = None
    if request.method == 'POST':
        pass
    else:
        list_all_order = partialEmployeeScanOrder()
    return render(request, 'basic_app/staff_in_China_mange_page.html', {'list_all_order':list_all_order })

@login_required
@staffInChina_required
def StaffInChinaOrderInDetails(request):
    pic_src = None
    dic = None
    OrderNum = None
    pic_src = None
    if request.method == 'POST':
        OrderNum = request.POST.get('orderID','-1')
        if (OrderNum != '-1'):      
            dic = chinaQuery(OrderNum)
            if (dic):
                pic_src = dic['Attached_picture']
                dic = dict(itertools.islice(dic.items(),1, len(dic)))
                del dic['Attached_picture']
        else:
            imageName = request.POST.get('image')
            secondNum = request.POST.get('secondNumber')
            ChinaEmployeeUpdatePicture(secondNum, imageName)
            return redirect(reverse('basic_app:StaffInChinaManagement'))
    else:
        print("this is not POST")


    return render(request, 'basic_app/staff_in_China_order_detail.html', {'dic':dic, 'pic_src':pic_src} )

@login_required
@supervisor_or_staffInUSA_required
def SupervisorProofView(request):
    listOfProof = None
    if request.method  == 'POST':
        pass
    else:
        listOfProof = partialScanProof()

    return render(request, 'basic_app/supervisor_proof_view.html', {'listOfProof':listOfProof})

@login_required
@supervisor_or_staffInUSA_required
def proofDetailsView(request):
    pic_src = None
    dic = None
    if request.method == 'POST':
        Num = request.POST.get('number','-1')
        dic = queryProof(Num)
        if (dic != None):
            pic_src = dic['Attached_picture']
            if (pic_src):
                del dic['Attached_picture']
            dic = dict(itertools.islice(dic.items(),1, len(dic)))
    else:
        pass
    return render(request, 'basic_app/proof_view_page.html', {'dic':dic, 'pic_src': pic_src})
