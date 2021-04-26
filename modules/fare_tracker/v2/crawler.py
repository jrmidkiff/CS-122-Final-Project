'''  crawler.py

This modules contains functions that will calculate route information about traveling to
different cities in the US. 

It uses faredetective.com to gather its data. 

'''
import re
import platform 
from selenium import webdriver
import time
_AIRFARE_URL = "https://www.faredetective.com/farehistory/"

_DATA_DICT_DEFAULT = {"to_city": [], "from_city": [], "fare": []}


def crawl(cities=[]):
    '''
        Crawls the faredective website and places the average fare prices inside the
        context provided.

        Args:
            cities([string]) - a list of cities to update in the fare context while crawling.
                                [] list represents to update all the popular destintations
    '''
    if platform.system() == 'Linux':
        from selenium.webdriver.firefox.options import Options
        driver_options = Options()
        driver_options.add_argument("--headless")
        driver_options.add_argument("--window-size=1920x1080")
        driver = webdriver.Firefox(options=driver_options)
    elif platform.system() == 'Darwin':
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        driver = webdriver.Chrome(options=chrome_options)

    print("Crawling route data...")
    driver.get(_AIRFARE_URL)
    popular_dest_links = driver.find_elements_by_xpath("//td/a")
    data_dict = _DATA_DICT_DEFAULT

    for i in range(len(popular_dest_links)):
        link = driver.find_elements_by_xpath("//td/a")[i]
        m = re.search(r"Airfares\s*to\s*(.+)", link.text)
        if m:
            to_city = m.group(1).strip()
            if not cities or to_city in cities:
                link.click()
                time.sleep(1)
                row = 1
                while True:
                    tab_link = driver.find_elements_by_xpath(
                        f"//table[@class='table table-history']/tbody/tr[{row}]/td[1]/a")

                    fare_elm = driver.find_elements_by_xpath(
                        f"//table[@class='table table-history']/tbody/tr[{row}]/td[@class='text-right']")
                    row += 1
                    if tab_link:
                        m = re.search(
                            r"Airfares\sfrom\s([\w\d\s]+)\s\(", tab_link[0].text)
                        if m:
                            from_city = m.group(1).strip()
                            if fare_elm:
                                m = re.search(r'\$(\d+)', fare_elm[0].text)
                                if m:
                                    fare = round(float(m.group(1).strip()), 2)
                                    # Update data_dict with all the data
                                    data_dict["from_city"].append(from_city)
                                    data_dict["to_city"].append(to_city)
                                    data_dict["fare"].append(fare)
                    else:
                        break
                driver.back()
                time.sleep(1)
    return data_dict

if __name__ == "__main__":
    print(crawl("Chicago"))