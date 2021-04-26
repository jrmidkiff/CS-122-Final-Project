''' tracker.py

This is an application module that allows a user to find information about
specific routes.
'''
from context import RouteContext
import sys

MENU = '''
********* Route Tracker *********
Welcome to the route tracker application! Please choose
an option to perform a task.

(1) List all route information
(2) Search a for a specific route
(3) Quit the program
'''
START = 1
END = 3


def find_route(cxt):
    print("\n---Find Route---")
    from_city = input("Enter in the from city: ")
    to_city = input("Enter in the to city: ")
    route = cxt[from_city, to_city]
    if route:
        print(f"\nRoute: {route}")
    else:
        print(
            f"ERROR: Could not find route information for {from_city} -> {to_city}")


def retrieve_task():
    option = -1
    while True:
        print(MENU)
        option = int(input("Option: "))
        if option >= START and option <= END:
            break
        else:
            print(f"Invalid option({option})")
    return option


OPTIONS_HANDLER = {
    1: lambda cxt: print(f"\n---All Route Information---\n{cxt}"),
    2: lambda cxt: find_route(cxt)
}

def main():
    # Process command line arguments
    # Note: Better to use the argparse module to handle command line arguments!
    delete = True
    print(sys.argv)
    if len(sys.argv) == 2:
        if sys.argv[1] == "False":
            delete = False

    # Create the route context object
    cxt = RouteContext(delete=delete)
    while True:
        option = retrieve_task()
        if option == 3:
            cxt.save()
            break
        else:
            handler = OPTIONS_HANDLER[option]
            handler(cxt)


if __name__ == "__main__":
    # This is the entry point into the application
    main()
