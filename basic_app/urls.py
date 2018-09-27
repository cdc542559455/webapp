from django.urls import path
from . import views
from django.contrib.auth import authenticate, login

# SET THE NAMESPACE!
app_name = 'basic_app'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('signup/',views.SignUp.as_view(),name='signup'),
    path('CustomerProofSearch/', views.CustomerProofSearch, name='CustomerProofSearch'),
    path('CustomerInvoiceSearch/', views.CustomerInvoiceSearch, name='CustomerInvoiceSearch'),
    path('StaffInUSAMangement/', views.CustomerInUSAOrderPage, name='StaffInUSAMangement'),
    path('OrderCreating/', views.OrderCreatePage, name='OrderCreating'),
    path('InvoiceCreate/', views.CreateInvoice, name='InvoiceCreate'),
    path('StaffInChinaManagement/', views.StaffInChinaManagement, name='StaffInChinaManagement'),
    path('StaffInChinaOrderView/', views.StaffInChinaOrderInDetails, name='StaffInChinaOrderView'),
    path('StaffInUSAInvoicemangement/', views.invoiceCreatePage, name = 'StaffInUSAInvoicemangement'),
    path('SupervisorProofView/', views.SupervisorProofView, name="SupervisorProofView"),
]
