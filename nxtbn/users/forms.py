
from django import forms

from allauth.utils import (
    set_form_field_order,
)
from allauth.account.forms import  SignupForm

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.utils.translation import gettext_lazy as _


class AllauthSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(AllauthSignupForm, self).__init__(*args, **kwargs)
        self.fields["first_name"] = forms.CharField(
            label=_("Fist Name"),
            max_length=255,
            widget=forms.TextInput(
                attrs={"placeholder": _("Fist Name"), "autocomplete": "Fist Name"}
            ),
        )

        self.fields["last_name"] = forms.CharField(
            label=_("Last Name"),
            max_length=255,
            widget=forms.TextInput(
                attrs={"placeholder": _("Last Name"), "autocomplete": "Fist Name"}
            ),
        )


        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    field_order = [
        "email",
        'first_name',
        'last_name',
        "password1",
        "password2",  # ignored when not present
    ]

