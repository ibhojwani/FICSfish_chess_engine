from django.shortcuts import render
from django.http import HttpResponse
from django import forms

from . import models

import ui.filtering_db as filtering_db

# Create your views here.

class SearchForm(forms.Form):
    BlackEloRangeStart = forms.IntegerField(min_value=600)
    BlackEloRangeEnd = forms.IntegerField(max_value=3000)
    WhiteEloRangeStart = forms.IntegerField(min_value=600)
    WhiteEloRangeEnd = forms.IntegerField(max_value=3000)

    # TODO: extend is_valid method to do your own validation

def form_view(request):
    # the user is loading the page
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            # do stuff with the data here

            filtered = models.Games.filter(BlackElo__gte=data['BlackEloRangeStart'],
                                           BlackElo__lte=data['BlackEloRangeEnd'],
                                           WhiteElo__gte=data['WhiteEloRangeStart'],
                                           WhiteElo__lte=data['WhiteEloRangeEnd'])

            return HttpResponse(data)
        else:
            return HttpResponse('your input was bad and you should feel bad')
    if request.method == 'GET':
        form = SearchForm()
    return render(request, 'form.html', {'form': form})
