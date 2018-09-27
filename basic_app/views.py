import itertools
from django.shortcuts import render, get_object_or_404, redirect, render
from .forms import StaffSignUpForm
from django.utils.decorators import method_decorator
from .decorators import customer_required, staffInChina_required, staffInUSA_required, supervisor_required
# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, ListView, UpdateView, TemplateView
from .dbFinalVersion import customerQueryProof, customerQueryInvoice, partialEmployeeScanOrder
from .upsBackEnd import initializeParas, getOptionWithTime, makeServiceWithPrice, getMinOption
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
        dic = customerQueryProof(value)
        if (dic != None):
            pic_src = dic['Attached_picture']
            dic = dict(itertools.islice(dic.items(),1, len(dic)))
    else:
        print("Is not Post")
    
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
        print(totalamout)
        hasPost = True
    else:
        print('Is not Post FFFF')

    return render(request, 'basic_app/customer_invoice_search.html', {'hasPost': hasPost, 'dic':dic, 'list1': list1, 'totalamout': totalamout} )

@login_required
@staffInUSA_required
def CustomerInUSAOrderPage(request):
    list_all_order = None
    if request.method == 'POST':
        # to add new row order
        pass
    else:
        list_all_order = partialEmployeeScanOrder()
    return render(request, 'basic_app/staff_in_usa_order_page.html', {'list_all_order':list_all_order })

@login_required
@staffInUSA_required
def OrderCreatePage(request):
    if request.method == 'POST':
        orderID = request.POST.get('orderID', '-1')
        input = request.POST.dict()
        print(type(orderID))
        if(orderID == '-1'):
            print("yes")
            listInput = list(input.values())
            listInput = listInput.pop(0)
            print(listInput)
            print(listInput)
            print(type(listInput))
        else:
            pass
    else:
        pass
    return render(request, 'basic_app/order_create.html')

@login_required
@staffInUSA_required
def CreateInvoice(request):
    result = 'No option for this pickUpDate and deliveyDate'
    if request.method == 'POST':
        #print("You Succeed!")
        initializeParas(request.POST)
        li = getOptionWithTime()
        makeServiceWithPrice(li)
        res = getMinOption(li)
        if len(res) > 1:
            #print(res)
            result = res[0]+', deliveried by '+res[4]+' at '+res[5]+' with '+res[8]+' '+res[9]
        pass
    else:
        pass
    return render(request, 'basic_app/staff_in_usa_create_invoice.html', {'result':result})

