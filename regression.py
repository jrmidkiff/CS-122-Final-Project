'''
BoardGameGeek Regression Prediction and Recommendation
CAPP 122 Final Project

Author: Syeda Jaisha

The following script runs a regression using data from BoardGameGeek (BGG) and
uses it to predict BGG rating and number of user reviews/ratings received, 
for a game designed by our user as well as to make recommendations on possible 
ways to improve the game rating and increase its popularity
'''

import pandas as pd
import numpy as np

rating_lst = ['avg_playtime', 'suggested_numplayers', 'averageweight', 
                'num_mechanics', 'lang_dep2', 'lang_dep3', 'lang_dep4', 
                'lang_dep5', 'Strategy Game', 'Family Game', 'Party Game', 
                'Abstract Game', 'Thematic', 'War Game','Customizable', 
                "Children's Game"]
popularity_lst = ['num_categories', 'num_mechanics', 'lang_dep2', 
                    'lang_dep3', 'lang_dep4', 'lang_dep5', 'Strategy Game', 
                    'Family Game', 'Party Game', 'Abstract Game', 'Thematic',
                    'War Game','Customizable', "Children's Game"]
django_to_local_cols = {'Average playing time': 'avg_playtime',
                        'Recommended number of players': 'suggested_numplayers',
                        'Complexity': 'averageweight',
                        'Number of categories': 'num_categories',
                        'Number of mechanics': 'num_mechanics',
                        'Language dependency' : {'lang_dep2': 2,
                                                'lang_dep3': 3,
                                                'lang_dep4': 4,
                                                'lang_dep5': 5 },
                        'Type': ['Strategy Game', 'Family Game', 'Party Game', 
                                'Abstract Game', 'Thematic', 'War Game',
                                'Customizable', "Children's Game"]}

def predict(input_dict, rating_bool):
    '''
    Main function that runs the regression and produces either predicted BGG 
    rating or number of ratings received and make relevant recommendations to
    improve upon the same.

    Inputs:
        rating_bool (bool): If True, run the regression for predicted BGG 
                            rating
                            If False, run the regression for predicted number
                            of ratings
        input_dict (dict): Dictionary produced by Django UI, containing 
                            required fields for the prediction using regression
    Output:
        (tuple of lists) Contains a list of column names and a list of columns
        output for Django UI

    Warning: Predicted values may be negative due to low R2 of models
    '''

    x = construct_x(input_dict, rating_bool)
    X, y, raw_df, dep_var = construct_X_y(rating_bool)
    coef = regress(X,y)
    beta = coef['beta']
    pred_val = apply_beta(beta, x)[0]
    accuracy = calculate_R2(X, y, beta)
    sorted_df_y = raw_df.sort_values(by=dep_var, ascending = False).\
        reset_index(drop=True)
    rank = sorted_df_y[sorted_df_y[dep_var] >= pred_val].index[-1] + 2
    top_5_games = ''
    for i, game in enumerate(sorted_df_y['name'][0:5]):
        top_5_games += game
        if i != 4:
            top_5_games += ', '
    decrease_gain_tup, increase_gain_tup, lang_dep_gain_tup, game_type_tup = \
        recommend(coef, input_dict, X, rating_bool)

    if rating_bool:
        return (['Your game is likely to get a BGG rating of ____ on BoardGameGeek',
                'placing you at a rank of ____ among 4093 games in our dataset',
                'with top 5 BGG board games being ____',
                'This prediction is only ____ percent accurate.',
                'try decreasing ____,' 
                'to improve score by (for each unit decreased) ____',
                'try increasing ____,' 
                'to improve score by (for each unit increased) ____',
                'try changing "Language dependency" to ____,'
                'to improve score by ____',
                'try dropping "type" _____,' 
                'try adding "type" _____, to improve score by ____'],
                [[str(round(pred_val,5)), rank,
                top_5_games, str(round(accuracy,2)), decrease_gain_tup,
                increase_gain_tup, lang_dep_gain_tup, game_type_tup]])
    else:
        return (['Your game is likely to be voted for by ____ users on BoardGameGeek',
                'placing you at a ____ rank among 4093 games in our dataset',
                'with top 5 BGG board games being _____',
                'This prediction is only ____ percent accurate.',
                'try decreasing ____,' 
                'to improve score by (for each unit decreased) ____',
                'try increasing ____,'
                'to improve score by (for each unit increased) ____',
                'try changing "Language dependency" to ____,'
                'to improve score by ____',
                'try dropping "type" _____, try adding "type" _____,'
                'to improve score by ____'],
                [[str(round(pred_val,0)), rank,
                top_5_games,str(round(accuracy,2)), decrease_gain_tup,
                increase_gain_tup, lang_dep_gain_tup, game_type_tup]])


def construct_x(input_dict, rating_bool):
    '''
    Construct x vector using user inputs from Django by matching Django 
    fields to column names in internal data, using field inputs to create 
    required columns and finally add a 'ones' column for constant of the 
    regression equation.

    Input: (dict) Dictionary produced by Django UI, containing 
            required fields for the prediction using regression
    Output: (pandas Series) Column vector 
    '''

    x_dict = {}
    type_lst =[]

    for field in input_dict.keys():
        if field == 'Language dependency':
            for dummy, complexity in django_to_local_cols[field].items():
                x_dict[dummy] = 0
                if input_dict[field] == complexity: 
                    x_dict[dummy] = 1
        elif field in ['Type 1', 'Type 2', 'Type 3']:
            type_lst.append(input_dict[field])
        else:
            col_name = django_to_local_cols[field]
            value = input_dict[field]
            x_dict[col_name] = value

    for type_dummy in django_to_local_cols['Type']:
        x_dict[type_dummy] = 0
        if type_dummy in type_lst:
          x_dict[type_dummy] = 1  
    
    x = pd.DataFrame(x_dict, index = ['obs'])

    if rating_bool:
        pred_vars = rating_lst
    else:
        pred_vars = popularity_lst

    x = x.loc[:,pred_vars]
    prepend_ones_col(x)

    return x 


def construct_X_y(rating_bool):
    '''
    Process raw data (data cleaning, data type coercion, creating dummy 
    variables) pulled from BoardGameGeek API and then use it to construct X 
    matrix and y vector to be plugged into the regress function. 

    Input: (bool) Indicates which regression model to run
    Outputs:
        X: (pandas DataFrame) X matrix containing observations of regressors
        y: (pandas Series) column vector containing obsersvations of dependent
        variable
        raw_df: (pandas DataFrame) processed dataframe
        dep_var: (str) name of depedent variable
    '''

    raw_df = pd.read_csv("all_games.csv")
    raw_df = raw_df.loc[:,['bgg_id', 'is_boardgame', 'name', 'name_coerced',
                        'minplaytime', 'maxplaytime', 'suggested_numplayers',
                        'suggested_language', 'num_ratings',
                        'Board Game_avg_rating', 'Strategy Game',
                        'Family Game', 'Party Game', 'Abstract Game', 'Thematic', 
                        'War Game','Customizable', "Children's Game", 
                        'num_categories', 'num_mechanics','averageweight']]
    raw_df = raw_df[raw_df['is_boardgame'] == True]
    raw_df = raw_df.dropna(subset=['suggested_language'])
    create_lang_dummy(raw_df)
    raw_df = raw_df.astype({'Strategy Game':'int64', 'Family Game': 'int64', 
                            'Party Game': 'int64', 'Abstract Game': 'int64',
                            'Thematic': 'int64', 'War Game': 'int64',
                            'Customizable': 'int64', "Children's Game": 'int64',
                            'lang_dep2': 'int64', 'lang_dep3': 'int64',
                            'lang_dep4': 'int64', 'lang_dep5': 'int64'})
    raw_df['suggested_numplayers'] = raw_df['suggested_numplayers']\
        .astype('string').str.strip('+').astype('int64')
    raw_df['avg_playtime'] = (raw_df['minplaytime'] + raw_df['maxplaytime'])/2
    raw_df = raw_df[raw_df['suggested_numplayers'] != 0]
    raw_df = raw_df[raw_df['avg_playtime'] != 0]
    raw_df = raw_df.dropna()
    
    if rating_bool:
        pred_vars, dep_var = rating_lst, 'Board Game_avg_rating'
    else:
        pred_vars, dep_var = popularity_lst, 'num_ratings'
    X = raw_df.loc[:,pred_vars]
    prepend_ones_col(X)
    y = raw_df[dep_var]

    return X, y, raw_df, dep_var


def create_lang_dummy(df):
    '''
    Create and insert (k-1) dummy variables for k Language dependency categories
    in the dataframe.

    Input: (pandas DataFrame) BGG data
    '''

    lang_dep = {'No necessary in-game text':1, 
           'Some necessary text - easily memorized or small crib sheet':2,
           'Moderate in-game text - needs crib sheet or paste ups':3,
           'Extensive use of text - massive conversion needed to be playable':4,
           'Unplayable in another language':5}

    categories = pd.unique(df['suggested_language'])
    for category in categories:
        if lang_dep[category] != 1:
            dummy_name = 'lang_dep' + str(lang_dep[category])
            df[dummy_name] = df['suggested_language'] == category


def prepend_ones_col(X):
    '''
    Add a ones column to the left side of pandas DataFrame.

    Input: (pandas DataFrame) X matrix
    '''
    X.insert(0,'ones', 1)


def regress(X, y):
    '''
    Regress X matrix on y vector and calculate beta vector.

    Inputs:
        X (pandas DataFrame): X matrix containing observations of regressors
        y (pandas Series): y vector 
    Ouputs:
        coef (pandas DataFrame): beta vector containing coefficient estimates 
        for the regressors

    '''
 
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    #Source: /home/syedajaisha/capp30121-aut-20-syedajaisha/pa5/util.py
    col_names = list(X.columns)
    col_names[0] = 'intercept'
    coef = pd.DataFrame({'beta': beta}, index=col_names)
    return coef


def calculate_R2(X, y, beta):
    '''
    Calculate R_sqauared for a regression model

    Inputs:
        X (pandas DataFrame): X matrix
        y (pandas Series): y vector
        beta(pandas DataFrame): beta vector
    Output: (float) R_squared
    '''

    yhat = apply_beta(beta, X)
    R2 = 1 - (np.sum((y - yhat)**2) / np.sum((y - np.mean(y))**2))
    #Source: /home/syedajaisha/capp30121-aut-20-syedajaisha/pa5/regression.py
    return R2*100


def apply_beta(beta, X):
    '''
    Apply beta, the vector generated by regress, to the
    specified values to calculate predicted value

    Inputs:
        beta (pandas Series): beta vector
        X (pandas DataFrame): X matrix
    Output:
        yhat (numpy array): predicted value
    '''

    yhat = np.dot(X, beta)
    return yhat
    

def recommend(coef, input_dict, X, rating_bool):
    '''
    Make recommendations based on what paramters can the user potentially 
    increase, decrease, switch categories of to increase their predicted value 
    of BGG rating and number of ratings and also informs of the corresponding 
    change in the predicted value

    Inputs:
        coef (pandas DataFrame): beta vector containing coefficient estimates 
        input_dict (dict): Dictionary produced by Django UI, containing 
                            required fields for the prediction using regression
        X (pandas DataFrame): X matrix
        rating_bool (bool): Indicates which regression model to run

    Disclaimer: This function doesn't recommend changing everything to arrive at
    the optimal result. For example, in case a game already has three types, it 
    won't suggest the user to replace them all with the ones corresponding to 
    the largest three coefficents among all games types, it would just ask that 
    the existing type that adds the least value to the regression be replaced 
    with the type corresponding to the highest coefficient among remaining game
    types
    '''

    dummy_var = ['Language dependency', 'Type']
    decrease_gain_tup = []
    increase_gain_tup =[]
    lang_dep_gain_tup = []
    game_type_tup= []

    if rating_bool:
        beta = round(coef['beta'],4)
    else:
        beta = round(coef['beta'],0).astype('int64')

    for field in django_to_local_cols:
        if field not in dummy_var:
            if field in input_dict:
                if beta[django_to_local_cols[field]] < 0:
                    if input_dict[field] > min(X[django_to_local_cols[field]]):
                        decrease_gain_tup.append((field, -beta[django_to_local_cols[field]]))
                else:
                    if input_dict[field] < max(X[django_to_local_cols[field]]):
                        increase_gain_tup.append((field, beta[django_to_local_cols[field]]))
        elif field == 'Language dependency':
            current_lang_dep = 'lang_dep' + str(input_dict['Language dependency'])
            if current_lang_dep == 'lang_dep1':
                for lang_dep_dummy in django_to_local_cols['Language dependency'].keys():
                    if beta[lang_dep_dummy] > 0:
                        lang_dep_gain_tup.append((django_to_local_cols['Language dependency'][lang_dep_dummy], \
                            beta[lang_dep_dummy]))
            else:
                if beta[current_lang_dep] < 0:
                    lang_dep_gain_tup.append((1, -beta[current_lang_dep]))
                for lang_dep_dummy in django_to_local_cols['Language dependency'].keys():
                    if beta[lang_dep_dummy] > beta[current_lang_dep]:
                        gain = -beta[current_lang_dep] + beta[lang_dep_dummy]
                        lang_dep_gain_tup.append((django_to_local_cols['Language dependency'][lang_dep_dummy], gain))
        elif field == 'Type':
            current_type_coefs = {}
            game_type_coefs = {}
            for game_type in django_to_local_cols['Type']:
                if game_type in input_dict.values():
                    current_type_coefs[beta[game_type]] = game_type
                else:
                    game_type_coefs[beta[game_type]] = game_type
            max_game_type_coef = max(game_type_coefs.keys())
            if len(current_type_coefs) == 3:
                min_current_type_coef = min(current_type_coefs.keys()) 
                if max_game_type_coef > min_current_type_coef:
                    game_type_tup.append((current_type_coefs[min_current_type_coef],
                                        game_type_coefs[max_game_type_coef],
                                        max_game_type_coef - min_current_type_coef))
            else:
                if max_game_type_coef > 0:
                    game_type_tup.append(('none',
                                        game_type_coefs[max_game_type_coef],
                                        max_game_type_coef))

    lst_lst = [decrease_gain_tup, increase_gain_tup, lang_dep_gain_tup, game_type_tup]
    for lst in lst_lst:
        if not lst:
            lst.append('already optimal')

    return (decrease_gain_tup, increase_gain_tup, lang_dep_gain_tup, game_type_tup)



                        
