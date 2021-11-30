# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from GoogleEngine import GoogleEngine

search_string = '("Intrusion Detection" ) AND Learning AND (Adversarial OR Evasion OR "Attack Models" OR "Covert ' \
                'Attack" OR "Stealthy Attack") '
year_interval = [2011, 2021]
scraper_key = '82bde596b52900f4c1910a1eebd2e999'
google_search = GoogleEngine(scraper_key)

google_search.search(search_string, year_interval)
google_search.df.to_csv('venue_files/google/google.csv')
