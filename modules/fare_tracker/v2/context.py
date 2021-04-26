''' context.py

This a module contains a class that manages the data about the
fare for multiple routes.

'''
import pandas as pd
from crawler import crawl
from route import Route

_DATA_FILE = "resources/data/routes.csv"


class RouteContext:
    '''
    A RouteContext manages the loading, saving, and querying of
    the fares for routes.
    '''

    def __init__(self, delete=True, cities=["Albuquerque", "Atlanta"]):
        '''
        Initializes the route context

        Args:
           update (bool) - True, update the fare information
                           for all cities
        '''
        if delete:
            self._df = pd.DataFrame(crawl(cities),
                                    columns=['from_city', 'to_city', 'fare'])
        else:
            self._df = pd.read_csv(_DATA_FILE)

    def save(self):
        '''
          Saves the context to its data storage.
        '''
        self._df.to_csv(_DATA_FILE, index=False)

    def __getitem__(self, item):
        if isinstance(item, (str, tuple)):
            from_city, to_city = item
            mask = (self._df["from_city"] == from_city) & (
                self._df["to_city"] == to_city)
            route = self._df[mask]
            if len(route) == 1:
                return Route(from_city, to_city, self._df["fare"][0])
            return None
        raise TypeError(
            f"Argument 'item' must be of type str tuple, not {type(item)}")

    def __str__(self):
        cxt_str = ""
        for row in self._df.itertuples():
            cxt_str += str(Route(row.from_city, row.to_city, row.fare)) + "\n"
        return cxt_str
