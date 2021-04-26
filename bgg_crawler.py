"""
CAPP 30122: Board Game Geek Game ID Crawler

Onel Abreu
"""
# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg=invalid-name, redefined-outer-name, unused-argument, unused-variable

import csv
import bs4
import pandas
import requests

def go(num_games_to_crawl, index_filename):
    '''
    Crawl the BoardGameGeek website rankings by num_voters and generates a CSV file 
    with the ordered rankings by game_id.

    Inputs:
        num_games_to_crawl: the number of games to process during the crawl;
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index.
    '''
    # figure out the total number of pages to traverse, 
    # where each page has 100 games listed
    if num_games_to_crawl <= 100:
        num_pages_to_crawl = 1
    else:
        num_pages_to_crawl = 1 + num_games_to_crawl//100

    game_ids_texts = []
    game_count = 0

    # iterate through each page and scrape game ID/description until we
    # reach num_games_to_crawl; then transform into dataframe/csv
    for page in range(1, num_pages_to_crawl + 1):
        url = "https://boardgamegeek.com/browse/boardgame/page/" + str(page) + "?sort=numvoters&sortdir=desc"
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.text, "html5lib")
        body_text = soup.tbody.select("tr", id_="row_")
        for row in body_text[1:]:
            if game_count < num_games_to_crawl:
                game_count += 1
                game_id = row.find("a", class_="primary")["href"].split("/")[2]
                text_exists = row.find("p", class_="smallefont dull")
                if text_exists:
                    game_text = text_exists.get_text().strip()
                else:
                    game_text = ""
                game_ids_texts.append((game_id, game_text))
            else: 
                break

    df = pandas.DataFrame(game_ids_texts, columns=["Game_ID", "Game_Text"])
    df.to_csv(index_filename, index=False, header=False)