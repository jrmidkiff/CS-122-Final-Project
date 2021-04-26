''' route.py
  This module provide an implementation of a Route class with operations
  that work on creating, and storing route information.
'''

# Prior Version using @datclass but this requires 3.7+ which is not by default in the
# VM so I changed it to use a normal class definition.

#from dataclasses import dataclass

# @dataclass  # @dataclass only avaliable in Python 3.7+
# class Route:
#    '''
#      A Route class contains information about a propsed route
#      for a flight
#    '''
#    from_city: str
#    to_city: str
#    fare: float

#   def __str__(self):
#       return f'From:{self.from_city} To:{self.to_city} -> Lowest Price: ${self.fare:.2f}'


class Route:
    ''' 
      A Route class contains information about a propsed route 
      for a flight
    '''

    def __init__(self, from_city, to_city, fare):
        self.from_city = from_city
        self.to_city = to_city
        self.fare = fare

    def __str__(self):
        return f'From:{self.from_city} To:{self.to_city} -> Lowest Price: ${self.fare:.2f}'
