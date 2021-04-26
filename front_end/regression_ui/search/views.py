'''
CAPP30122 W'21: Group Project - Regression UI/Website
Author: Onel Abreu
'''

import json
import traceback
import sys
import csv
import os

from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

from regression import predict

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')

COLUMN_NAMES = dict(
    min_playtime='Min Playtime',
    max_playtime='Max Playtime',
    game_name="Game Name",
    difficulty="Difficulty",
    game_type="Game Type(s)",
    game_cats="Game Categories",
    game_mecs="Game Mechanisms",
    players="Num Players",
    min_players="Min Players",
    max_players="Max Players",
    play_time="Playing Time",
    age="Min Age",
    preference="Search Preference",
    lang_dept="Language Dependency"
)

def _valid_result(res):
    """Validate results returned by game_search."""
    (HEADER, RESULTS) = [0, 1]
    ok = (isinstance(res, (tuple, list)) and
            len(res) == 2 and
            isinstance(res[HEADER], (tuple, list)) and
            isinstance(res[RESULTS], (tuple, list)))
    if not ok:
        return False
    else:
        return True
    #n = len(res[HEADER])
    
    #def _valid_row(row):
    #    return isinstance(row, (tuple, list)) and len(row) == n
    #return reduce(and_, (_valid_row(x) for x in res[RESULTS]), True)

def _load_column(filename, col=0):
    """Load single column from csv file."""
    with open(filename) as f:
        col = list(zip(*csv.reader(f)))[0]
        return list(col)

def _load_res_column(filename, col=0):
    """Load column from resource directory."""
    return _load_column(os.path.join(RES_DIR, filename), col=col)

def _build_dropdown(options):
    """Convert a list to (value, caption) tuples."""
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]


DIFFICULTY = _build_dropdown(_load_res_column('difficulty.csv'))
GAMETYPE = _build_dropdown([None] + _load_res_column('game_type.csv'))
GAMECATEGORY = _build_dropdown(_load_res_column('game_category.csv'))
GAMEMECHANISM = _build_dropdown(_load_res_column('game_mechanics.csv'))
PREFERENCES = _build_dropdown(_load_res_column('preference.csv'))
LANGUAGE = _build_dropdown([None] + _load_res_column('language.csv'))


RANGE_WIDGET = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput,
                                                  forms.widgets.NumberInput))

class SearchForm(forms.Form):
    '''
    Utilize Django forms to create dropdown menus

    Inputs: User defined through web interface per variable below
    Outputs: None (updates form.cleaneddata attribute with saved user inputs)
    '''
    preference = forms.ChoiceField(label='Prediction Preference',
                help_text='Choose one',
                choices=PREFERENCES,
                widget=forms.RadioSelect,
                required=True)
    game_type1 = forms.ChoiceField(label='Type 1',
                choices=GAMETYPE, required=True)
    game_type2 = forms.ChoiceField(label='Type 2',
                choices=GAMETYPE, required=True)   
    game_type3 = forms.ChoiceField(label='Type 3',
                choices=GAMETYPE, required=True)
    language = forms.ChoiceField(label='Language Dependency', 
                choices=LANGUAGE, required=True)
    game_mecs = forms.IntegerField(label='Number of Mechanics',
                help_text='Max of 20',
                min_value=1,
                max_value=20,
                required=True)   
    game_cats = forms.IntegerField(label='Number of Categories',
                help_text='Max of 14',
                min_value=1,
                max_value=14,
                required=True)
    time = forms.IntegerField(label='Average Playing Time',
                help_text='In minutes',
                min_value=1,
                max_value=2400,
                required=True)
    players = forms.IntegerField(label='Recommended # Players',
                help_text='Max of 20',
                min_value=1,
                max_value=20,
                required=True)
    complexity = forms.IntegerField(label='Complexity',
                help_text='1-5 with "1" being the least, "5" being the most complex',
                min_value=1,
                max_value=5,
                required=True)    

    show_args = forms.BooleanField(label='Show args_to_ui',
                                   required=False)


def home(request):
    '''
    Creates a webpage view that validates form data input by a user, converts that
    data into a input dictionary, and uses that input dictionary as an argument
    for the function that will create a table of results for the user.

    Inputs:
        request: request object for web interfacing
    Outputs:
        Rendered webpage table of results from the assigned function
    '''
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():

            # Convert form data to an args dictionary for regression prediction
            args = {}

            preference = form.cleaned_data["preference"]
            if preference == "Ratings":
                rating_bool = True
            else:
                rating_bool = False
            
            lang_num = 0
            language = form.cleaned_data["language"]
            if language == "No necessary in-game text":
                lang_num = 1
            if language == "Some necessary text - easily memorized or small crib sheet":
                lang_num = 2
            if language == "Moderate in-game text - needs crib sheet or paste ups":
                lang_num = 3
            if language == "Extensive use of text - massive conversion needed to be playable":
                lang_num = 4
            if language == "Unplayable in another language":
                lang_num = 5
            args["Language dependency"] = lang_num

            game_type1 = form.cleaned_data['game_type1']
            if game_type1:
                args['Type 1'] = game_type1

            game_type2 = form.cleaned_data['game_type2']
            if game_type2:
                args['Type 2'] = game_type2

            game_type3 = form.cleaned_data['game_type3']
            if game_type3:
                args['Type 3'] = game_type3

            mechanics = form.cleaned_data['game_mecs']
            if mechanics:
                args['Number of mechanics'] = mechanics  

            if rating_bool:
                num_player = form.cleaned_data['players']
                if num_player: 
                    args['Recommended number of players'] = num_player   
                time = form.cleaned_data['time']
                if time:
                    args['Average playing time'] = time
                complexity = form.cleaned_data["complexity"]
                if complexity:
                    args["Complexity"] = complexity        
            else:
                game_cats = form.cleaned_data['game_cats']
                if game_cats:
                    args['Number of categories'] = game_cats  

            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui = ' + json.dumps(args, indent=2)
            
            form = SearchForm()
            
            try:
                res = predict(args, rating_bool)
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in predict:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))

                res = None
    else:
        form = SearchForm()

    # Handle different responses of res
    if res is None:
        context['result'] = None
    elif isinstance(res, str):
        context['result'] = None
        context['err'] = res
        result = None
    elif not _valid_result(res):
        context['result'] = None
        context['err'] = ('Return of predict has the wrong data type. '
                          'Should be a tuple of length 4 with one string and '
                          'three lists.')
    else:
        columns, result = res

        # Wrap in tuple if result is not already
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]

    context['form'] = form
    return render(request, 'index.html', context)