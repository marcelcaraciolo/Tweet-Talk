# -*- coding: utf-8 -*-

from django import forms

class PinCodeForm(forms.Form):
    pin_code = forms.CharField(max_length=12)