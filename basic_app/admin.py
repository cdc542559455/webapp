from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .forms import StaffSignUpForm, StaffSignUpChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = StaffSignUpForm
    form = StaffSignUpChangeForm
    model = CustomUser
    list_display = ['email' , 'username', 'user_type', 'is_customer', 'is_staffInChina', 'is_staffInUSA', 'is_supervisor']

admin.site.register(CustomUser, CustomUserAdmin)

