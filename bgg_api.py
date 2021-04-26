'''
This script pulls data about boardgames from the BoardGameGeek (BGG) API, gathers 
the data, and exports it in various files and formats. 

Author: James Midkiff
Course: CAPP 30122 Final Project
Date: March, 2021
'''
import re
import pandas as pd
import requests 
import bs4
import json
import csv
import time

def go(file_in, limit=5000, size=100, start=1, file_suffix_out=""): 
    '''
    Overall function to pull data from BoardGameGeek API. 
    
    This function includes a mandatory wait time of 5 seconds. At limit=5000, 
    size=100, start=0, this function takes approximately 11 minutes to run. 

    Inputs: 
        file_in (str): Name of file that contains game IDs and short descriptions
        limit (int): Number of entries to pull from API. 
        size (int): Size of chunks to send to API at any one time. There's a 
            trade-off between efficiency and sending too large of a chunk to the 
            API. Size >= 500 is known to cause bad responses from the API. 
        start (int): Index number to begin at. Primarily used for debugging. 
        file_suffix_out (str): Suffix to add to all filenames out, such as 
            "_actual", "_test", etc. Default = "", which is used for full data pull. 
    Outputs: 
        1) Writes all game information to JSON file. 
        2) Calls function to write all game information (limiting to 10 most 
            popular categories and mechanics) to CSV file. 
        3) Calls function to write game type counts to CSV file. 
        4) Calls function to write game categories counts to CSV file. 
        5) Calls function to write game mechanics counts to CSV file. 
    '''
    ids = import_ids(file_in)
    
    start = start
    end = min(start + size - 1, limit)
    games_dict = {}
    types_dict = {}
    categories_dict = {}
    mechanics_dict = {}
    print(f"\nObtaining BoardGameGeek information for top {limit} IDs by number of votes")
    while True:
        print(f'Pulling IDs {start}-{end}')
        batch = ",".join(list(ids.loc[start - 1:end - 1,"ID"]))
        # print(batch)
        print("~~~~~~~~~~~~")
        soup = call_api(batch)
        short_descriptions = ids.loc[start - 1:end - 1]
        get_game_info(soup, games_dict, 
            types_dict, categories_dict, mechanics_dict, short_descriptions)
        start += size
        end = start + size
        if end > len(ids) or end > limit:
            end = min(len(ids), limit)
        if start > limit:
            break
        time.sleep(5)
    
    with open(f"all_games{file_suffix_out}.json", "w") as out_file:
        json.dump(games_dict, out_file, indent=6)
    # with open(f"all_games{file_suffix_out}.json", "r") as in_file:
    #     test = json.load(in_file)

    construct_csv(games_dict, types_dict, categories_dict, mechanics_dict, 
        file_suffix_out)
    # data = pd.read_csv(f"all_games{file_suffix_out}.csv")

    filepath_t = create_extra_csv(types_dict, "types", file_suffix_out)
    filepath_c = create_extra_csv(categories_dict, "categories", file_suffix_out)
    filepath_m = create_extra_csv(mechanics_dict, "mechanics", file_suffix_out)
    # types_df = pd.read_csv(f"types_counts{file_suffix_out}.csv").sort_values("count", ascending=False)
    # categories_df = pd.read_csv(f"categories_counts{file_suffix_out}.csv").sort_values("count", ascending=False)
    # mechanics_df = pd.read_csv(f"mechanics_counts{file_suffix_out}.csv").sort_values("count", ascending=False)
    print(f'\nData Pull Complete!\n')
    print(f'    CSV of game information: all_games{file_suffix_out}.csv')
    print(f'    JSON of game information: all_games{file_suffix_out}.json')
    print(f'    CSV of game type counts: {filepath_t}')
    print(f'    CSV of game category counts: {filepath_c}')
    print(f'    CSV of game mechanic counts: {filepath_m}\n')


def import_ids(filename): 
    '''
    Imports file of BGG game IDs and short_descriptions

    Inputs: 
        filename (str): Name of file that contains game IDs and short descriptions
    
    Outputs: 
        Pandas DataFrame
    '''
    ids = pd.read_csv(filename, header=None, names=["ID", "short_description"])
    ids["ID"] = ids["ID"].astype("str")
    ids["short_description"] = ids['short_description'].fillna("[No Description]")
    return ids


def call_api(ids_str): 
    '''
    Function that generates URL and calls BGG API

    Inputs: 
        ids_str (str): String sequence of boardgame IDs to send to API as parameter
    
    Outputs: 
        soup (bs4.BeautifulSoup): bs4 API response to parse. 
    '''
    url_api = "http://www.boardgamegeek.com/xmlapi/boardgame/"
    response = requests.get(url_api + ids_str + "?stats=1")
    if response.status_code != requests.codes.ok: 
        response.raise_for_status()
    text = response.text
    soup = bs4.BeautifulSoup(text, features="html5lib")
    return soup


def get_game_info(soup, games_dict, types_dict, categories_dict, mechanics_dict, 
    short_descriptions): 
    '''
    Gathers information for each game from the API response. 

    Inputs: 
        soup (bs4.BeautifulSoup): bs4 API response to parse. 
        games_dict (dict): Dictionary to add boardgame information to
        types_dict (dict): Dictionary to add counts of game types to. 
        categories_dict (dict): Dictionary to add counts of game categories to
        mechanics_dict (dict): Dictionary to add counts of game mechanics to
        short_descriptions (Pandas DataFrame): Dataframe of short-descriptions to 
            include in game information
    
    Outputs: 
        None: Updates games_dict, types_dict, categories_dict, and mechanics_dict 
            in place. 
    '''
    for game in soup.find_all("boardgame"): 
        bgg_id = game["objectid"]
        # print("--------") 
        # print(f'BGG_ID: {bgg_id}') 
            # Something really weird is happening between
            # ids 1589 and 155731 (indices 2608 and 2609) - five IDs for non-games
            # are getting inserted in the soup: 141023, 141024, 140248-14250.
            # It looks like they have an additional attribute {'inbound': 'true'}
        if "inbound" not in game.attrs.keys() and games_dict.get(bgg_id) is None: 
            try: 
                name = game.find("name", attrs={"primary":"true"}).text
                # print(f'Game Name: {name}') 
                name_coerced = re.sub(
                    pattern="\W", repl="", string=name.upper().strip())
                yearpublished = game.yearpublished.text
                shortdescription = (short_descriptions.query(f'ID == "{bgg_id}"')
                    ["short_description"].values[0])
                minplayers = game.minplayers.text
                maxplayers = game.maxplayers.text
                playingtime = game.playingtime.text
                minplaytime = game.minplaytime.text
                maxplaytime = game.maxplaytime.text
                age = game.age.text
                
                suggested_playerage = None 
                suggested_playerage_votes = -1 # Don't include in output
                playerage_poll = game.find("poll", 
                    attrs={"name":"suggested_playerage"})
                if playerage_poll["totalvotes"] != "0": 
                    for option in playerage_poll.results.find_all("result"):
                        playerage = option["value"]
                        numvotes = int(option["numvotes"])
                        if numvotes > suggested_playerage_votes: 
                            # With ties, take minimum age
                            suggested_playerage = playerage
                            suggested_playerage_votes = numvotes
                    
                suggested_numplayers = None
                suggested_numplayers_votes = -1 # Don't include in output
                numplayers_poll = game.find("poll", 
                    attrs={"name":"suggested_numplayers"})
                if numplayers_poll["totalvotes"] != "0": 
                    for option in numplayers_poll.find_all("results"):
                        numplayers = option["numplayers"]
                        suggested_tag = option.find("result", attrs={"value": "Best"})
                        votes = int(suggested_tag["numvotes"])
                        if votes >= suggested_numplayers_votes: 
                            # With ties, take maximum numplayers
                            suggested_numplayers = numplayers
                            suggested_numplayers_votes = votes
                
                suggested_language = None
                suggested_language_votes = -1 # Don't include in output
                language_poll = game.find("poll", 
                    attrs={"name": "language_dependence"})
                if language_poll["totalvotes"] != "0": 
                    for option in language_poll.results.find_all("result"): 
                        language = option["value"] 
                        # option["level"] increases with each game called - that's dumb
                        numvotes = int(option["numvotes"])
                        if numvotes >= suggested_language_votes: 
                            # With ties, take maximum language dependency
                            suggested_language = language
                            suggested_language_votes = numvotes
                
                num_ratings = int(game.statistics.ratings.usersrated.text)
                geek_rating = float(game.statistics.ratings.average.text)
                
                bgg_type_info = {}
                num_types = 0
                for rank in game.statistics.ratings.ranks.find_all("rank"):
                    bgg_type_name = re.findall(
                        pattern="^.+(?=\sRank)", string=rank["friendlyname"])[0]
                    if bgg_type_name != "Board Game":
                        num_types += 1
                    bgg_type_rating = float(rank["bayesaverage"])
                    bgg_type_rank = rank["value"]
                    bgg_type_info[bgg_type_name] = (bgg_type_rating, bgg_type_rank)
                    types_dict[bgg_type_name] = types_dict.get(bgg_type_name, 0) + 1

                categories = [] # JSON can't deal with sets, unfortunately
                is_boardgame = True
                not_game_categories = {"Expansion for Base-game", "Fan Expansion", 
                    "Game System"} 
                num_categories = 0
                for cat in game.find_all("boardgamecategory"): 
                    category = cat.text
                    if category in not_game_categories: 
                        is_boardgame = False
                    categories.append(category)
                    num_categories += 1
                    categories_dict[category] = categories_dict.get(category, 0) + 1

                mechanics = []
                num_mechanics = 0
                for mech in game.find_all("boardgamemechanic"):
                    mechanic = mech.text
                    mechanics.append(mechanic)
                    num_mechanics += 1
                    mechanics_dict[mechanic] = mechanics_dict.get(mechanic, 0) + 1
                
                averageweight = float(game.statistics.averageweight.text)
                long_description = game.description.text
                image_url = game.img.next_sibling.strip("\n\t")

                games_dict[bgg_id] = {}
                games_dict[bgg_id]["is_boardgame"] = is_boardgame
                games_dict[bgg_id]["name"] = name
                games_dict[bgg_id]["name_coerced"] = name_coerced
                games_dict[bgg_id]["yearpublished"] = yearpublished
                games_dict[bgg_id]["shortdescription"] = shortdescription
                games_dict[bgg_id]["minplayers"] = minplayers
                games_dict[bgg_id]["maxplayers"] = maxplayers
                games_dict[bgg_id]["playingtime"] = playingtime
                games_dict[bgg_id]["minplaytime"] = minplaytime
                games_dict[bgg_id]["maxplaytime"] = maxplaytime
                games_dict[bgg_id]["age"] = age
                games_dict[bgg_id]["suggested_playerage"] = suggested_playerage
                games_dict[bgg_id]["suggested_numplayers"] = suggested_numplayers
                games_dict[bgg_id]["suggested_language"] = suggested_language
                games_dict[bgg_id]["num_ratings"] = num_ratings
                games_dict[bgg_id]["geek_rating"] = geek_rating
                games_dict[bgg_id]["num_types"] = num_types
                games_dict[bgg_id]["bgg_type_info"] = bgg_type_info # dict
                games_dict[bgg_id]["num_categories"] = num_categories
                games_dict[bgg_id]["categories"] = categories # list
                games_dict[bgg_id]["num_mechanics"] = num_mechanics
                games_dict[bgg_id]["mechanics"] = mechanics # list
                games_dict[bgg_id]["averageweight"] = averageweight
                games_dict[bgg_id]["long_description"] = long_description
                games_dict[bgg_id]["image_url"] = image_url
            except Exception as e: 
                print(repr(e))
                print(f'Script Failed at BGG_ID {bgg_id}')
                raise e
    

def construct_csv(games_dict, types_dict, categories_dict, mechanics_dict, 
    file_suffix_out): 
    '''
    Writes game information (limiting to 10 most popular categories and 
    mechanics) to CSV file. Calls construct_fields() which creates the CSV header.

    Inputs: 
        games_dict (dict): Dictionary with boardgame information
        types_dict (dict): Dictionary with counts of game types
        categories_dict (dict): Dictionary with counts of game categories
        mechanics_dict (dict): Dictionary with counts of game mechanics
        file_suffix_out (str): Suffix to add to all filenames out, such as 
            "_actual", "_test", etc. Default = "", which is used for full data pull. 
    
    Outputs: 
        Writes all game information (limiting to 10 most popular categories and 
            mechanics) to CSV file. 
    '''
    fields, categories_cols, mechanics_cols = construct_fields(
        types_dict, categories_dict, mechanics_dict)
    
    with open(f'all_games{file_suffix_out}.csv', 'w') as f: 
        csvwriter = csv.writer(f)
        csvwriter.writerow(fields)
        
        for bgg_id, info in games_dict.items(): 
            data = []
            data.append(bgg_id)
            data.extend([
                info["is_boardgame"], 
                info["name"], 
                info["name_coerced"], 
                info["yearpublished"], 
                info["shortdescription"], 
                info["minplayers"], 
                info["maxplayers"], 
                info["playingtime"], 
                info["minplaytime"], 
                info["maxplaytime"], 
                info["age"], 
                info["suggested_playerage"], 
                info["suggested_numplayers"], 
                info["suggested_language"], 
                info["num_ratings"], 
                info["geek_rating"], 
                info["num_types"]])
            
            for type in types_dict.keys(): 
                if type in info["bgg_type_info"].keys(): 
                    subrating, subrank = info["bgg_type_info"][type]
                    data.extend([True, subrating, subrank])
                else: 
                    data.extend([False, False, False])
            
            data.append(info["num_categories"])
            for category in categories_cols: 
                if category in info["categories"]:
                    data.append(True)
                else: 
                    data.append(False)
            
            data.append(info["num_mechanics"])
            for mechanic in mechanics_cols: 
                if mechanic in info["mechanics"]:
                    data.append(True)
                else: 
                    data.append(False)
        
            data.extend([
                info["averageweight"], 
                info["long_description"], 
                info["image_url"]])
            
            csvwriter.writerow(data)


def construct_fields(types_dict, categories_dict, mechanics_dict): 
    '''
    Constructs the header fields for CSV file written in construct_csv().

    Inputs: 
        types_dict (dict): Dictionary with counts of game types
        categories_dict (dict): Dictionary with counts of game categories
        mechanics_dict (dict): Dictionary with counts of game mechanics
    
    Outputs: 
        fields (list of str): List of field names
        categories_cols (list of str): List of top 10 categories (excluding 
            "Expansion for Base-game" to be used for analysis) to be used as 
            column headers
        mechanics_cols (list of str): List of top 10 mechanics to be used as 
            column headers
    '''
    fields = ["bgg_id", 
        "is_boardgame", 
        "name", 
        "name_coerced", 
        "yearpublished", 
        "shortdescription", 
        "minplayers", 
        "maxplayers", 
        "playingtime", 
        "minplaytime", 
        "maxplaytime", 
        "age", 
        "suggested_playerage", 
        "suggested_numplayers", 
        "suggested_language", 
        "num_ratings", 
        "geek_rating", 
        "num_types"]
    
    for gametype in types_dict.keys(): 
        fields.extend([gametype, gametype + "_avg_rating", gametype + "_rank"]) 
    
    fields.append("num_categories")        
    categories_cols = []
    categories_df = pd.DataFrame.from_dict(
        data=categories_dict, orient="index", columns=["Count"])
    categories_df = categories_df.sort_values(
        by="Count", ascending=False, axis="index")
    categories_list = (list(categories_df
        .loc[categories_df.index != "Expansion for Base-game"]
        .index.values[0:10]))    # Don't include above category. Ties for top 10 
                                # broken arbitrarily 
    fields.extend(categories_list)
    categories_cols.extend(categories_list)
    
    fields.append("num_mechanics")

    mechanics_cols = []
    mechanics_df = pd.DataFrame.from_dict(
        data=mechanics_dict, orient="index", columns=["Count"])
    mechanics_list = list(mechanics_df
        .sort_values(by="Count", ascending=False, axis="index") 
        .index.values[0:10]) # Ties for 10 broken arbitrarily
    fields.extend(mechanics_list)
    mechanics_cols.extend(mechanics_list)

    fields.extend([
        "averageweight", 
        "long_description", 
        "image_url"])    
    
    return fields, categories_cols, mechanics_cols
    

def create_extra_csv(obj, name, file_suffix_out): 
    '''
    Creates an extra CSV from a dictionary of type (key, value) with filename 
    becoming "name_counts.csv" and first column named "name". 

    Inputs: 
        obj (dict): Dictionary of type (key, value)
        name (str): Name of key
        file_suffix_out (str): Suffix to add to all filenames out, such as 
            "_actual", "_test", etc. Default = "", which is used for full data pull. 
    
    Outputs: 
        Writes information to CSV. 
        Returns filepath (str) for debugging. 
    '''
    filepath = f'{name}_counts{file_suffix_out}.csv'
    with open(filepath, 'w') as f: 
        csvwriter = csv.writer(f)
        header = [name, "count"]
        csvwriter.writerow(header)
        for key, value in obj.items(): 
            csvwriter.writerow([key, value])
    
    return filepath