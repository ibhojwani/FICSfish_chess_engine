from django.shortcuts import render
from django.http import HttpResponse
from django import forms

from . import models

import ui.filtering_db as filtering_db

# Create your views here.

class SearchForm(forms.Form):
    min_B_ELO = forms.IntegerField(min_value=600,required=False,\
        label='Minimum Black ELO Rating',)

    max_B_ELO = forms.IntegerField(max_value=3000,required=False,\
        label='Maximum Black ELO Rating')
    min_W_ELO = forms.IntegerField(min_value=600,required=False,\
        label='Minimum White ELO Rating')
    max_W_ELO = forms.IntegerField(max_value=3000,required=False,\
        label='Maximum White ELO Rating')
    num_plays_cutoff = forms.IntegerField(min_value=0,required=False,\
        label='Number of Plays Cutoff')
    first_play_white = forms.CharField(max_length=3,required=False, \
        label='Opening Move - White')
    first_play_black = forms.CharField(max_length=3,required=False, \
        label='Opening Move - Black')
    gameID_box = forms.BooleanField(required=False, label=\
        'Would you like a list of the game IDs for the FICS online database?')


def form_view(request):
    # the user is loading the page
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            stats = filtering_db.get_statistics(data)
            # do stuff with the data here
            return HttpResponse(data)
        else:
            return HttpResponse('Your inputs were incorrect and the form cannot\
                be processed. Please re-enter valid inputs.')

    if request.method == 'GET':
        form = SearchForm()
    return render(request, 'form.html', {'form': form})
