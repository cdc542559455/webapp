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
def CustomerSearch(request):
    hasPost = False
    if request.method == 'POST':
        value = request.POST.get('orderNumber')
        firstname = request.POST.get('firstName')
        lastname = request.POST.get('lastName')
        print("The Order Number is:"+str(value))
        print("The firstName is:"+str(firstname))
        print("The lastname is:"+str(lastname))
    else:
        print("Is not Post")
    
    return render(request, 'basic_app/customer_search.html')