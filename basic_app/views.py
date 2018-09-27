import itertools
from unipath import Path
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
from .dbFinalVersion import customerQueryProof, customerQueryInvoice, partialEmployeeScanOrder, customerQueryOrder, showFullOrder, ChinaEmployeeUpdatePicture, generateOrUpdateOrderAndProof
import itertools

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
    listpart = None
    newCompound = None
    if request.method == 'POST':
        orderID = request.POST.get('orderID', '-1')
        input = request.POST.dict()
        del input['csrfmiddlewaretoken']
        if(orderID == '-1'):
            listInput = list(input.values())
            print(type(listInput))
            fistpart = listInput[:14]
            print("**************************************************")
            secondpart = listInput[14:]
            print(secondpart)
            kk = dict(itertools.zip_longest(*[iter(secondpart)]*2, fillvalue=""))
            print("**************************************************")
            print(fistpart)
            print("**************************************************")
            print(kk)
            print("**************************************************")
            fistpart.append(kk)
            print(type(kk))
            print("**************************************************")
            print(type(listInput))
            print("**************************************************")
            print(fistpart)
            print("**************************************************")
            generateOrUpdateOrderAndProof(fistpart)


        else:
            listpart,dictpart = showFullOrder(orderID)
            print("this is edit page")
            print("attribute lengh"+str(len(listpart)))
            extraRow = len(dictpart)
            print(extraRow)
            print(dictpart)
            namelist = list(range(15,15+2*extraRow+1))
            namelist = namelist[::2]
            container = []
            for key, value in dictpart.items():
                temp = [key, value]
                container.append(temp)
            newCompound = dict(zip(namelist,container))
            print(newCompound)            
    else:
        pass
    return render(request, 'basic_app/order_create.html', {'listpart':listpart, 'newCompound': newCompound })

@login_required
@staffInUSA_required
def CreateInvoice(request):
    result = None
    if request.method == 'POST':
        print("You Succeed!")
        pass
    else:
        pass
    return render(request, 'basic_app/staff_in_usa_create_invoice.html', {'result':result})

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
        print(OrderNum)
        pic_src = request.POST.get('myImage')
        if (pic_src != None):
            ChinaEmployeeUpdatePicture('666', Path(pic_src).absolute())
            print(Path(pic_src).absolute())
            print('go through it')
            return redirect(reverse('basic_app:StaffInChinaManagement'))
            
        else:
            print("this is POST Operation")
            print(request.POST.dict())
            print(type(OrderNum))
            print(OrderNum)
            if (OrderNum != '-1'):
                dic = customerQueryOrder(OrderNum)
                if (dic != None):
                    pic_src = dic['Attached_picture']
                    dic = dict(itertools.islice(dic.items(),1, len(dic)))
    else:
        print("this is not POST")


    return render(request, 'basic_app/staff_in_China_order_detail.html', {'dic':dic, 'pic_src':pic_src} )

