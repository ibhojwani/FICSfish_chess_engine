from django.shortcuts import render
from django.http import HttpResponse
from django import forms

from . import models

import ui.filtering_db as filtering_db

# Create your views here.

class SearchForm(forms.Form):
    BlackEloRangeStart = forms.IntegerField(min_value=600,required=False)
    BlackEloRangeEnd = forms.IntegerField(max_value=3000,required=False)
    WhiteEloRangeStart = forms.IntegerField(min_value=600,required=False)
    WhiteEloRangeEnd = forms.IntegerField(max_value=3000,required=False)
    NumPlaysCutoff = forms.IntegerField(min_value=0,required=False)
    FirstPlay = forms.CharField(max_length=10,required=False)
    GameList = forms.BooleanField(required=False) 


def form_view(request):
    # the user is loading the page
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            # do stuff with the data here
            return HttpResponse(data)
        else:
            return HttpResponse('Your input was incorrect. Please re-enter the values and click Submit.')
            return HttpResponse(data)
        else:
            return HttpResponse('Your inputs were incorrect and the form cannot\
                be processed. Please re-enter valid inputs.')

    if request.method == 'GET':
        form = SearchForm()
    return render(request, 'form.html', {'form': form})
