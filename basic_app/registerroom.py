from django.shortcuts import redirect, render
from django.views.generic import TemplateView

class SignUpView(TemplateView):
    template_name = 'basic_app/signup.html'

def home(request):
    if request.user.is_authenticated:
        if request.user.is_customer:
            pass
        else:
            pass
    return render(request, 'basic_app/index.html')            