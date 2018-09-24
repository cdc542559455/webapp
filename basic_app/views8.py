# users/views.py
from django.urls import reverse_lazy
from django.views import generic

from .forms import StaffSignUpForm
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request,'basic_app/index.html')

class SignUp(generic.CreateView):
    form_class = StaffSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('index'))
