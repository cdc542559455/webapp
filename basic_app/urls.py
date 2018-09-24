from django.urls import path
from . import views
from django.contrib.auth import authenticate, login

# SET THE NAMESPACE!
app_name = 'basic_app'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('signup/',views.SignUp.as_view(),name='signup'),
    path('customer_search/', views.CustomerSearch, name='customer_search')
]
