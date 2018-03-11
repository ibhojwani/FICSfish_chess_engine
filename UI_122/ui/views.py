from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import ui.database_tools as dbt

from . import models

import ui.filtering_db as filtering_db


class SearchForm(forms.Form):
    min_B_ELO = forms.IntegerField(min_value=600,required=False,\
        label='Minimum Black ELO Rating',initial=800, help_text=\
        'Please input a number between 600 and 3000. If this field is empty,\
        the default value will be 800.')

    max_B_ELO = forms.IntegerField(max_value=3000,required=False,\
        label='Maximum Black ELO Rating',initial=2600,help_text='\
        Please input a number between 600-3000. If this field is empty,\
        the default value will be 2600.')
    
    min_W_ELO = forms.IntegerField(min_value=600,required=False,\
        label='Minimum White ELO Rating',initial=800,help_text='\
        Please input a number between 600 and 3000. If this field is empty,\
        the default value will be 800.')

    max_W_ELO = forms.IntegerField(max_value=3000,required=False,\
        label='Maximum White ELO Rating',initial=2600,help_text='\
        Please input a number between 600-3000. If this field is empty,\
        the default value will be 2600.')

    num_plays_cutoff = forms.IntegerField(min_value=0,required=False,\
        label='Number of Plays Cutoff',initial=50)
    
    first_play_white = forms.CharField(max_length=3,required=False, \
        label='Opening Move - White') #not initialized
    
    first_play_black = forms.CharField(max_length=3,required=False, \
        label='Opening Move - Black') #not initialized
    
    result = forms.IntegerField(required=False,label='Result of Game') 
    #not initialized

    gameID_box = forms.BooleanField(required=False, label=\
        'Would you like a list of the game IDs for the FICS online database?')
    
    hist_plot = forms.BooleanField(required=False, label =\
        'Would you like to see the distribution of ELO Ratings from our database?',\
        initial=False)

def form_view(request):
    # the user is loading the page
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            #converting data with default values 
            output = {}
            if form.cleaned_data['min_B_ELO']:
                output['min_B_ELO'] = form.cleaned_data['min_B_ELO']
            else:
                output['min_B_ELO'] = 600

            if form.cleaned_data['max_B_ELO']:
                output['max_B_ELO'] = form.cleaned_data['max_B_ELO']
            else:
                output['max_B_ELO'] = 3000

            if form.cleaned_data['min_W_ELO']:
                output['min_W_ELO'] = form.cleaned_data['min_W_ELO']
            else:
                output['min_W_ELO'] = 600

            if form.cleaned_data['max_W_ELO']:
                output['max_W_ELO'] = form.cleaned_data['max_W_ELO']
            else:
                output['max_W_ELO'] = 3000

            if form.cleaned_data['num_plays_cutoff']:
                output['num_plays_cutoff'] = form.cleaned_data['num_plays_cutoff']
            else:
                output['num_plays_cutoff'] = 100

            if form.cleaned_data['result']:
                output['result'] = form.cleaned_data['result']

            if form.cleaned_data['first_play_white']:
                white_integer = dbt.convert_to_int(data['first_play_white'])
                output['first_play_white'] = white_integer

            if form.cleaned_data['first_play_black']:
                black_integer = white_integer = dbt.convert_to_int(data['first_play_black'])

            #call function here
            return HttpResponse(output)
        else:
            return HttpResponse('Your inputs were incorrect and the form cannot\
                be processed. Please re-enter valid inputs.')

    if request.method == 'GET':
        form = SearchForm()
    return render(request, 'form.html', {'form': form})
