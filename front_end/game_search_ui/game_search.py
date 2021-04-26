'''
CAPP30122 W'21: Group Project

Domnigo Carbone
'''

import pandas as pd
import csv

def find_best_match(search_dict):
    """
    Receives a dictionary of inputs provided by a user in a Django interface, 
    which lists charachteristics of desirable titles, and filters a pre-processed
    database, returning a list of the top results matching the search criteria, 
    as well as detailing the type of game they are, the number and age of players 
    it's intended for, and the time they take to play.

    Input:
        search_dict: A dictionary representing the search terms input by the user.
    Output:
        A tuple of lists representing the top five games recomended to the user,
        given by search_dict, as well as a short description for each game.
    """
    games_df = pd.read_csv("all_games.csv")

    search_dict_rev = build_search_dict(search_dict)

    filtered_df = filter_game_df(search_dict_rev, games_df)

    return top_games(search_dict_rev, filtered_df)

def build_search_dict(search_dict):
    '''
    Builds a dictionary where each preference indicated by a user in search_dict
    is associated to an individual key, as well as associating all unmarked 
    preferences keys to False.

    Input:
        search_dict: A dictionary representing the search terms input by the user.
    Output:
        A dictionary listing all possible search categories, setting those unmarked
        by the user as "False", and assigning all other preferences to individual
        keys.
    
    '''
    final_dict = {"difficulty":False, "Abstract Game":False, \
    "Customizable":False, "Thematic":False, "Family Game":False, \
    "Children's Game":False, "Party Game":False, "Strategy Game":False, \
    "War Game":False, "age":False, "min_players":False, "max_players":False, \
    "min_playtime":False, "max_playtime":False, "Card Game":False, \
    "Fantasy":False, "Fighting":False, "Economic":False, \
    "Science Fiction":False, "Wargame":False, "Adventure":False, "Dice":False, \
    "Medieval":False, "Miniatures":False, "Hand Management":False, "Dice Rolling":False, \
    "Variable Player Powers":False, "Set Collection":False, 
    "Card Drafting":False, "Area Majority / Influence":False, 
    "Modular Board":False, "Tile Placement":False, "Cooperative Game":False, \
    "Grid Movement":False, "preference":False}

    for key, value in search_dict.items():

        if key == "difficulty":
            if len(value) == 2:
                if value == ["Low", "Moderate"]:
                    final_dict["difficulty"] =  "low_moderate"
                elif value == ["Moderate", "High"]:
                    final_dict["difficulty"] = "moderate_high"
                elif value ==["Low", "High"]:
                    final_dict["difficulty"] = "low_high"
            elif len(value) == 1:
                if value == ["Low"]:
                    final_dict["difficulty"] = "low"
                elif value == ["Moderate"]:
                    final_dict["difficulty"] = "moderate"
                elif value == ["High"]:
                    final_dict["difficulty"] = "high"
        elif key == "game_types":
            for type_ in value:
                if type_ == "Abstract":
                    final_dict["Abstract Game"] = True
                elif type_ == "Party":
                    final_dict["Party Game"] = True
                elif type_ == "Children's":
                    final_dict["Children's Game"] = True
                elif type_ == "Strategy":
                    final_dict["Strategy Game"] = True
                elif type_ == "Family":
                    final_dict["Family Game"] = True
                elif type_ == "Customizable":
                    final_dict["Customizable"] = True
                elif type_ == "Thematic":
                    final_dict["Thematic"] = True
                elif type_ == "War":
                    final_dict["War Game"] = True
        elif key == "min_age":
            final_dict["age"] = value      
        elif key == "min_players":
            final_dict["min_players"] = value
        elif key == "max_players":
            final_dict["max_players"] = value
        elif key == "min_playitme":
            final_dict["min_playtime"] = value
        elif key == "max_playtime":
            final_dict["max_playtime"] = value
        elif key == "game_cats":
            for cat in value:
                if cat == "Cards":
                    final_dict["Card Game"] = True
                elif cat == "Fantasy":
                    final_dict["Fantasy"] = True
                elif cat == "Fighting":
                    final_dict["Fighting"] = True
                elif cat == "Economic":
                    final_dict["Economic"] = True
                elif cat == "Sci-Fi":
                    final_dict["Science Fiction"] = True
                elif cat == "War":
                    final_dict["Wargame"] = True 
                elif cat == "Adventure":
                    final_dict["Adventure"] = True 
                elif cat == "Dice":
                    final_dict["Dice"] = True 
                elif cat == "Medieval":
                    final_dict["Medieval"] = True 
                elif cat == "Miniatures":
                    final_dict["Miniatures"] = True
        elif key == "game_mecs":
            for mec in value:
                if mec == "Dice Rolling":
                    final_dict["Dice Rolling"] = True
                elif mec == "Hand Management":
                    final_dict["Hand Management"] = True
                elif mec == "Variable Player Powers":
                    final_dict["Variable Player Powers"] = True
                elif mec == "Set Collection":
                    final_dict["Set Collection"] = True
                elif mec == "Card Drafting":
                    final_dict["Card Drafting"] = True
                elif mec == "Area Influence":
                    final_dict["Area Majority / Influence"] = True 
                elif mec == "Modular Board":
                    final_dict["Modular Board"] = True 
                elif mec == "Tile Placement":
                    final_dict["Tile Placement"] = True 
                elif mec == "Cooperative":
                    final_dict["Cooperative Game"] = True 
                elif mec == "Grid Movement":
                    final_dict["Grid Movement"] = True
        elif key == "preference":
            if value == ["Popularity"]:
                    final_dict["preference"] = "popularity"
            elif value == ["Ratings"]:
                    final_dict["preference"] = "ratings"
    return final_dict

def filter_game_df(search_dict, games_df):
    """
    Filters the board game database, eliminating all titles that don't meet any
    of the search criteria for a given parameter.

    Input: 
        search_dict: A dictionary representing the search terms input by the user
        games_df: A pandas dataframe with board game data.
    
    Output: A pandas dataframe, fitered for all the requests input by the user.
    """
    games_df.query("is_boardgame == True", inplace = True)

    if search_dict["difficulty"]:
        difficulty = search_dict["difficulty"]
        if difficulty == "low":
            games_df.query("averageweight < 2.5", inplace = True)
        elif difficulty == 'moderate':
            games_df.query("2.5 <= averageweight <= 3.5", inplace = True)
        elif difficulty == "high":
            games_df.query("averageweight >= 3.5", inplace = True)
        elif difficulty == "low_moderate":
            games_df.query("averageweight < 3.5", inplace = True)
        elif difficulty == "moderate_high":
            games_df.query("averageweight >= 2.5", inplace = True)
        elif difficulty == "low_high":
            games_df.query("averageweight < 2.5 | averageweight >= 3.5", \
            inplace = True)

    query_list = []
    query_list = build_query(query_list, search_dict, "Abstract Game")
    query_list = build_query(query_list, search_dict, "Customizable")
    query_list = build_query(query_list, search_dict, "Thematic")
    query_list = build_query(query_list, search_dict, "Family Game")
    query_list = build_query(query_list, search_dict, "Children's Game")
    query_list = build_query(query_list, search_dict, "Party Game")
    query_list = build_query(query_list, search_dict, "Strategy Game")
    query_list = build_query(query_list, search_dict, "War Game")

    if query_list != []:
        query_str = " | ".join(query_list)
        games_df.query(query_str, inplace = True)
    
    if search_dict["age"]:
        age = search_dict[age]
        games_df.query("age <= @age", inplace = True)

    if search_dict["min_players"]:
        min_players = search_dict["min_players"]
        games_df.query("minplayers >= @min_players", inplace = True)

    if search_dict["max_players"]:
        max_players = search_dict["max_players"]
        games_df.query("maxplayers <= @max_players", inplace = True)
    
    if search_dict["min_playtime"]:
        min_playtime = search_dict["min_playtime"]
        games_df.query("minplaytime >= @min_playtime", inplace = True)

    if search_dict["max_playtime"]:
        max_playtime = search_dict["max_playtime"]
        games_df.query("maxplaytime <= @max_playtime", inplace = True)

    query_list = []

    query_list = []
    query_list = build_query(query_list, search_dict, "Card Game")
    query_list = build_query(query_list, search_dict, "Fantasy")
    query_list = build_query(query_list, search_dict, "Fighting")
    query_list = build_query(query_list, search_dict, "Economic")
    query_list = build_query(query_list, search_dict, "Science Fiction")
    query_list = build_query(query_list, search_dict, "Wargame")
    query_list = build_query(query_list, search_dict, "Adventure")
    query_list = build_query(query_list, search_dict, "Dice")
    query_list = build_query(query_list, search_dict, "Medieval")
    query_list = build_query(query_list, search_dict, "Miniatures")

    if query_list != []:
        query_str = " | ".join(query_list)
        games_df.query(query_str, inplace = True)

    query_list = []
    query_list = build_query(query_list, search_dict, "Hand Management")
    query_list = build_query(query_list, search_dict, "Dice Rolling")
    query_list = build_query(query_list, search_dict, "Variable Player Powers")
    query_list = build_query(query_list, search_dict, "Set Collection")
    query_list = build_query(query_list, search_dict, "Card Drafting")
    query_list = build_query(query_list, search_dict, "Area Majority / Influence")
    query_list = build_query(query_list, search_dict, "Modular Board")
    query_list = build_query(query_list, search_dict, "Tile Placement")
    query_list = build_query(query_list, search_dict, "Cooperative Game")
    query_list = build_query(query_list, search_dict, "Grid Movement")

    if query_list != []:
        query_str = ' | '.join(query_list)
        games_df.query(query_str, inplace = True)
    
    return games_df

def build_query(query_list, search_dict, col_name):
    """
    Builds or extends a query string to be used in a pandas .query method.

    Input: 
        query_list = A list containing previous query strings.
        search_dict: A dictionary representing the search terms input by the user.
        col_name = A column name corresponding to search_dict.
    
    Output: An extended query_list.
    """

    if search_dict[col_name]:
        query_list.append("`" + col_name + "`" + "==True")
        
    return query_list 

def top_games(search_dict, filtered_df):
    """
    Finds the five titles that better fit a user's preference, given a search 
    dictionary and a pre-filtered dataframe, by taking into account the user's
    preference for ratings, popularity, or neither.

    Input: 
        search_dict: A dictionary representing the search terms input by the user.
        filtered_df: A pandas dataframe with board game data.
    Output:
        A tuple of lists representing the top five games recomended to the user,
        given by search_dict, as well as a short description for each game.
    """

    if search_dict["preference"] == "popularity":
        return (build_top_tuple(search_dict, filtered_df, "num_ratings"))

    elif search_dict["preference"] == "ratings":
        return(build_top_tuple(search_dict, filtered_df, "Board Game_avg_rating"))

    elif search_dict["preference"] == False:

        max_popularity = filtered_df["num_ratings"].max()
        max_rating = filtered_df["Board Game_avg_rating"].max()

        filtered_df["mixed_rating"] = (\
            (filtered_df["num_ratings"] / max_popularity) + \
            (filtered_df["Board Game_avg_rating"] / max_rating ) / 2)

        return(build_top_tuple(search_dict, filtered_df, "mixed_rating"))

def build_top_tuple(search_dict, filtered_df, col_name):
    """
    Finds the five titles that better fit a user's preference, given a search 
    dictionary, a pre-filtered dataframe, andn the user's preference for ratings,
    popularity, or neither.

    Input: 
        search_dict: A dictionary representing the search terms input by the user.
        filtered_df: A pandas dataframe with board game data.
        col_name: The name of the column the data is to be sorted by, representing
                  the user's preference for popularity, scores, or neither.   
    
    Output:
        A tuple of lists representing the top five games recomended to the user,
        given by search_dict, as well as a short description for each game.
    """

    list1 = ["Game Name", "Game Type(s)", "Min Players", "Max Players", \
    "Playing Time", "Min Age"]

    filtered_df.sort_values(by = [col_name], ascending = False, inplace = True)

    list2 = []
    
    for row in filtered_df.head(5).iterrows():
        entry_list = []
        entry_list.append(row[1]["name"])
        type_list = []
        if row[1]["Abstract Game"]:
            type_list.append("Abstract")
        if row[1]["Customizable"]:
            type_list.append("Customizable")
        if row[1]["Thematic"]:
            type_list.append("Thematic")
        if row[1]["Family Game"]:
            type_list.append("Family")
        if row[1]["Children's Game"]:
            type_list.append("Children's")
        if row[1]["Party Game"]:
            type_list.append("Party")
        if row[1]["Strategy Game"]:
            type_list.append("Strategy")
        if row[1]["War Game"]:
            type_list.append("War")
        entry_list.append(type_list)
        entry_list.append(row[1]["minplayers"])
        entry_list.append(row[1]["maxplayers"])
        entry_list.append(row[1]["playingtime"])
        entry_list.append(row[1]["age"])
        list2.append(entry_list)
    
    return (list1, list2)