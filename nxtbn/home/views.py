from django.shortcuts import render, redirect
from django.urls import reverse

from django.http import HttpResponse


def home(request):
    return redirect(reverse('api_docs'))
    # if request.user.is_authenticated:
    #     return redirect(reverse('api_playground'))
    # else:
    #     return redirect(reverse('account_login'))
