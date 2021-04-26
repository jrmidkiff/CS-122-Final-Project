'''
CAPP30122 W'21: Group Project - Game Search UI/Website
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

from game_search import find_best_match

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')

COLUMN_NAMES = dict(
    min_playtime='Min Playtime',
    max_playtime='Max Playtime',
    difficulty="Difficulty",
    game_type="Game Type(s)",
    game_cats="Game Categories",
    game_mecs="Game Mechanisms",
    players="Num Players",
    play_time="Playing Time",
    age="Min Age",
    preference="Search Preference"
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

    n = len(res[HEADER])
    
    def _valid_row(row):
        return isinstance(row, (tuple, list)) and len(row) == n
    return reduce(and_, (_valid_row(x) for x in res[RESULTS]), True)

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
GAMETYPE = _build_dropdown(_load_res_column('game_type.csv'))
GAMECATEGORY = _build_dropdown(_load_res_column('game_category.csv'))
GAMEMECHANISM = _build_dropdown(_load_res_column('game_mechanics.csv'))
PREFERENCES = _build_dropdown(_load_res_column('preference.csv'))


class IntegerRange(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.IntegerField())
        super(IntegerRange, self).__init__(fields=fields,
                                           *args, **kwargs)

    def compress(self, data_list):
        if data_list and (data_list[0] is None or data_list[1] is None):
            raise forms.ValidationError('Must specify both lower and upper '
                                        'bound, or leave both blank.')
        return data_list


class PlayerRange(IntegerRange):
    def compress(self, data_list):
        super(PlayerRange, self).compress(data_list)
        for v in data_list:
            if not 1 <= v <= 12:
                raise forms.ValidationError(
                    'Player bounds must be in the range 1 to 12.')
        if data_list and (data_list[1] < data_list[0]):
            raise forms.ValidationError(
                'Lower bound must not exceed upper bound.')
        return data_list


class PlaytimeRange(IntegerRange):
    def compress(self, data_list):
        super(PlaytimeRange, self).compress(data_list)
        for v in data_list:
            if not 1 <= v <= 6000:
                raise forms.ValidationError(
                    'Playtime bounds must be in the range 1 to 6000')
        if data_list and (data_list[1] < data_list[0]):
            raise forms.ValidationError(
                'Lower bound must not exceed upper bound.')
        return data_list


RANGE_WIDGET = forms.widgets.MultiWidget(widgets=
(forms.widgets.NumberInput(attrs={'style': 'border-color: blue;', 
        'placeholder': 'Minimum'}),
forms.widgets.NumberInput(attrs={'style': 'border-color: blue;', 
        'placeholder': 'Maximum'})))

class SearchForm(forms.Form):
    '''
    Utilize Django forms to create dropdown menus

    Inputs: User defined through web interface per variable below
    Outputs: None (updates form.cleaneddata attribute with saved user inputs)
    '''
    age = forms.IntegerField(
        label='Minimum Age to Play',
        widget=forms.NumberInput(attrs={'style': 'border-color: blue;', 
        'placeholder': 'e.g. 5 Years Old'}),
        required=False)
    players = PlayerRange(
        label='Number of players',
        widget=RANGE_WIDGET,
        required=False)
    time = PlaytimeRange(
        label='Playtime (in minutes)',
        widget=RANGE_WIDGET,
        required=False)
    difficulty = forms.MultipleChoiceField(label='Difficulty',
                choices=DIFFICULTY,
                widget=forms.CheckboxSelectMultiple,
                required=False)
    game_type = forms.MultipleChoiceField(label='Game Type',
                choices=GAMETYPE,
                widget=forms.CheckboxSelectMultiple,
                required=False)  
    game_cats = forms.MultipleChoiceField(label='Game Categories',
                choices=GAMECATEGORY,
                widget=forms.CheckboxSelectMultiple,
                required=False)   
    game_mecs = forms.MultipleChoiceField(label='Game Mechanisms',
                choices=GAMEMECHANISM,
                widget=forms.CheckboxSelectMultiple,
                required=False)                
    preference = forms.MultipleChoiceField(label='Sort Preference',
                choices=PREFERENCES,
                widget=forms.CheckboxSelectMultiple,
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
            cd = form.cleaned_data
            # Convert form data to an args dictionary for game_search
            args = {}

            num_player = cd['players']
            if num_player: 
                args['min_players'] = num_player[0]
                args['max_players'] = num_player[1]            
            
            time = cd['time']
            if time:
                args['min_playtime'] = time[0]
                args['max_playtime'] = time[1]
            
            age = cd['age']
            if age:
                args['age'] = age
                
            game_type = cd['game_type']
            if game_type:
                args['game_types'] = game_type
            
            game_cats = cd['game_cats']
            if game_cats:
                args['game_cats'] = game_cats
            
            mechanisms = cd['game_mecs']
            if mechanisms:
                args['game_mecs'] = mechanisms           

            difficulty = cd["difficulty"]
            if difficulty:
                args["difficulty"] = difficulty

            preference = cd["preference"]
            if preference:
                args["preference"] = preference

            if cd['show_args']:
                context['args'] = 'args_to_ui = ' + json.dumps(args, indent=2)

            try:
                res = find_best_match(args)
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in find_matches:
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
        context['err'] = ('Return of game_search has the wrong data type. '
                          'Should be a tuple of length 2 with one string and '
                          'one list of lists.')
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

    