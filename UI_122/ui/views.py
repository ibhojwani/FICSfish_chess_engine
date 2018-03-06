from django.shortcuts import render
from django.http import HttpResponse
from django import forms

from . import models

import ui.filtering_db as filtering_db


def form_view(request):
    # the user is loading the page
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
#            statistics_to_return = filtering_db.return_statistics(database.db, data)
            return HttpResponse(data)
        else:
            return HttpResponse('Your inputs were incorrect and the form cannot\
                be processed. Please re-enter valid inputs.')
    if request.method == 'GET':
        form = SearchForm()
    return render(request, 'form.html', {'form': form})
