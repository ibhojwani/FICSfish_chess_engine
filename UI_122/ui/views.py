from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from ui.translation import translate_moves_to_int
from . import models
import ui.filtering_db as filtering_db


class SearchForm(forms.Form):
    '''
    This search form is designed to take filtering suggestions from the user
    for the historical-data driven chess engine. 
    '''
    min_B_ELO = forms.IntegerField(min_value=0,required=False,\
        label='Minimum Black ELO Rating',initial=800)
    max_B_ELO = forms.IntegerField(max_value=3000,required=False,\
        label='Maximum Black ELO Rating',initial=2600)
    min_W_ELO = forms.IntegerField(min_value=0,required=False,\
        label='Minimum White ELO Rating',initial=800)
    max_W_ELO = forms.IntegerField(max_value=3000,required=False,\
        label='Maximum White ELO Rating',initial=2600)
    num_plays_cutoff = forms.IntegerField(min_value=0,required=False,\
        label='Number of Plays Cutoff',initial=50)
    #we are not initalizing result, if this is left blank, it's not included in filtering  
    result = forms.IntegerField(required=False,label='Result of Game')
    gameID_box = forms.BooleanField(required=False, label=\
        'Would you like a list of the game IDs for the FICS online database?')

def form_view(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            #this is the dictionary being returned to filtering_db.py

            output = {}

            if form.cleaned_data['min_B_ELO']:
                output['min_B_ELO'] = form.cleaned_data['min_B_ELO']
            else:
                output['min_B_ELO'] = 0

            if form.cleaned_data['max_B_ELO']:
                output['max_B_ELO'] = form.cleaned_data['max_B_ELO']
            else:
                output['max_B_ELO'] = 3000

            if form.cleaned_data['min_W_ELO']:
                output['min_W_ELO'] = form.cleaned_data['min_W_ELO']
            else:
                output['min_W_ELO'] = 0

            if form.cleaned_data['max_W_ELO']:
                output['max_W_ELO'] = form.cleaned_data['max_W_ELO']
            else:
                output['max_W_ELO'] = 3000

            if form.cleaned_data['num_plays_cutoff']:
                output['num_plays_cutoff'] = form.cleaned_data['num_plays_cutoff']
            else:
                output['num_plays_cutoff'] = 1000

            if form.cleaned_data['result']:
                output['result'] = form.cleaned_data['result']

            if form.cleaned_data['gameID_box']:
                output['gameID_box'] = True
            else:
                output['gameID_box'] = False


            stats = filtering_db.get_statistics(output)
            return HttpResponse(stats)
        else:
            return HttpResponse('Your inputs were incorrect and the form cannot \
                be processed. Please re-enter valid inputs.')

    if request.method == 'GET':
        form = SearchForm()
    return render(request, 'form.html', {'form': form})
