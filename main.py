'''
BoardGameGeek (BGG) Analysis

Project Authors: James Midkiff, Onel Abreu, Syeda Jaisha, Domingo Carbone

Date: March 2021

This file launches each project component and provides information about the project. 

Run this file via the commands: 
    python3 main.py
    - or - 
    python main.py
'''
import os
import time
import re
import bgg_crawler
import bgg_api


MENU = '''
* * * * * * * * * * * * * BoardGameGeek(BGG) Analysis * * * * * * * * * * * * * 

Welcome!

What would you like to do?
(1) View our Game Recommendation system
(2) View our Regression Prediction system
(3) Test the web scraping and API code
(4) View the 'About This Project' file
(5) Exit
        '''

def clear(): 
    '''
        Clears the terminal screen. Implementation comes from here: 
        https://www.geeksforgeeks.org/clear-screen-python/
    '''
    if os.name == 'nt': # for windows
        _ = os.system('cls') 
    else: # for mac and linux(here, os.name is 'posix') 
        _ = os.system('clear') 


def call_input(): 
    '''
        Asks for the user's input in the Main Menu
    '''
    user_input = input("Please type the corresponding key and press enter:\n")
    act(user_input)


def act(user_input): 
    '''
        Upon successful user input, calls the correct functions to execute the user's 
        preference. 
    '''
    if user_input not in {"1", "2", "3", "4", "5"}: 
        print(f"Input '{user_input}' not recognized. Please try again.\n")
        call_input()
    elif user_input == "1": 
        print("\n***The Django user-interface should display the option to 'Open in " + 
            "Browser'")
        print("Click that button to proceed.")
        print("***Press CONTROL-C to exit the server.\n")
        os.chdir("./front_end/game_search_ui")
        os.system("python3 manage.py runserver 8000")
        os.chdir("../..")
        return_main_menu()
    elif user_input == "2": 
        print("\n***The Django user-interface should display the option to 'Open in " + 
            "Browser'")
        print("Click that button to proceed.")
        print("***Press CONTROL-C to exit the server.\n")
        os.chdir("./front_end/regression_ui")
        os.system("python3 manage.py runserver 8080")
        os.chdir("../..")
        return_main_menu()
    elif user_input == "3": 
        test_code()
        return_main_menu()
    elif user_input == "4": 
        print_help()
        return_main_menu()
    elif user_input == "5": 
        print("\nThank you for using our application, goodbye!\n")
        time.sleep(1)
    

def test_code(): 
    '''
        Code to run a limited version of the scraping and API data extraction scripts. 

        Implementation came from here: 
        https://stackoverflow.com/questions/31737745/python-call-function-again-if-incorrect-input

        Outputs: 
            Five CSV files to the current directory as described in the file bgg_api.py
    '''
    clear()
    while True: 
        print("\nPlease indicate the number of boardgames to pull from the BGG API:")
        limit = input()
        try: 
            game_limit = int(limit)
            if game_limit <= 0: 
                print("\nNumber must be greater than 0. Please try again.")
            else: 
                break
        except ValueError or TypeError: 
            print(f"\nInput must be an integer. Please try again.")
    while True: 
        print("\nPlease provide a suffix to add to the names of the exported files.\n" + 
            "   i.e. _test, _example, etc.:")
        suffix = input()
        if suffix is None or re.sub(pattern="\W", repl="", string=suffix) == "": 
            print('Suffix must not be an empty string.')
        else: 
            break
    
    bgg_crawler.go(num_games_to_crawl=game_limit, 
        index_filename=f"game_ids_small_texts{suffix}.csv")
    
    bgg_api.go(file_in=f'game_ids_small_texts{suffix}.csv', 
        limit=game_limit, size=100, start=1, file_suffix_out=f'{suffix}')

    return_main_menu()


def return_main_menu(): 
    '''
        Return to the Main Menu
    '''
    input("\nPress enter to return to the Main Menu:\n")
    main()


def print_help(): 
    '''
        Prints the help file for this script
    '''
    clear()
    string = '''
    ***** About This Project *****

    This project was completed as part of the course requirements for CAPP 30122 
    in March 2021 by James Midkiff, Onel Abreu, Syeda Jaisha, and Domingo Carbone. 

    Main project components: 
    - Game Recommendation system: This recommends up to five boardgames that match 
        a user's preferences, sorting by mean user rating or by popularity. 

    - Regression Prediction system:  This predicts the mean user rating 
        and popularity for a hypothetical boardgame given the user's description. 

    - Web scraping and API testing application:  This tests the code used for 
        scraping web data and pulling API data from BoardGameGeek. 
    
    The game recommendation and regression predictions systems use a dataset 
    of the 5000 boardgames with the most number of ratings on the BoardGameGeek 
    website as of March 12, 2021. Game expansions were removed from the dataset. 

    The testing application allows the user to run the web scraping and the 
    API data scripts for a specified number of boardgames and visit the 
    corresponding exported files. In the interest of project stability, these 
    files are NOT used in the Game Recommendation or Regression Prediction systems; 
    their purpose is to allow the user to see how the data was obtained. 

    Project component authors: 
    - Game Recommendation system:  Domingo Carbone
    - Regression Prediction system:  Syeda Jaisha
    - Django/User-Interface:  Onel Abreu
    - API Data Extraction:  James Midkiff
    - Additional Web Scraping:  Onel Abreu
    - Project component linking:  James Midkiff
    
    All data and images come from the BoardGameGeek site, located at 
    boardgamegeek.com

    Thank you for exploring our application, and play more boardgames!
    '''
    print(string)
    

def main(): 
    '''
        Function to "generate" the main menu. 
    '''
    clear()
    print(MENU)
    call_input()

if __name__ == "__main__":
    # This is the entry point into the application
    main()