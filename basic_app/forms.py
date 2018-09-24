from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.db import transaction
from django.db import models
from django.urls import reverse
from crispy_forms.bootstrap import Field, InlineRadios, TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset


class StaffSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ( 'email' , 'username', 'user_type', )

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        #print("user type is: "+str(user.user_type))
        if (user.user_type == 1):
            user.is_active = True
            user.is_customer = True
    
        elif (user.user_type == 2):
            user.is_active = False
            user.is_staffInChina = True
        elif (user.user_type == 3):
            user.is_active =False
            user.is_staffInUSA = True
        else:
            user.is_active =False
            user.is_supervisor = True

        if commit:
            user.save()
        return user

class StaffSignUpChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ( 'email' , 'username', 'user_type', )

