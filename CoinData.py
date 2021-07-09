# Gets the data from xyz coins and outputs it structured.

import json # Import json library 
import os # Import the os library
import csv # Import CSV library
from datetime import datetime # Import datetime package
from pycoingecko import CoinGeckoAPI # Import coingecko API.
cg = CoinGeckoAPI() # Initialize CoinGecko api

# Class for coin operations
class Coin:

    # In hindsight I should have just made a config file.
    # I could have also omitted the date in both the market_cap and price array for my purposes but this still serves a purpose, I guess.
    coin_list = ["bitcoin", "algorand", "vechain", "iota", "monero", "tezos", "chainlink", "stellar", "cosmos", "polkadot"] # List of coins to get data from

    def __init__(self, currency: str, date: str):
        """ Initalizes the Coin object
        :param str currency: The currency in which the prices will be returned
        :param str date: The date from which to pull historical data from
        """
        self.vs_currency = currency # Currency to get price pairs from
        self.date = date # Start date for historical data
        self.output_csv = False # Output as CSV aswell?

        self.create_files() # Check if the necessary files already exist, else create them!

    def create_files(self):
        """Creates all the necessary files if they do not exist yet."""
        files = ["CoinData.json", "CoinData-Exported.json", "CoinData-Exported.csv"] # List of files + extension that we will need
        for f in files: # Iterate over file name list
            if not os.path.isfile(f): # If file not found
                open(f, "w+") # Create file
            
    def export_to_csv(self):
        """This will take all of our exported data (.json file) and turn it into csv format; coin,date,price,marketcap"""
        with open("CoinData-Exported.json", "r") as cd: # Open CoinData-Exported.json
            cd = json.load(cd) # Load json data
            with open("CoinData-Exported.csv", "w", newline="") as cf: # Open CoinData-Exported.csv
                cf.write("coin,date,price,marketcap\n") # Write the CSV columns
                writer = csv.writer(cf, delimiter=",") # Create a new CSV writer with , as a delimiter
                for c in cd: # Iterate over CoinData-Exported.json; c = coin
                        for (p, m) in zip(cd[c]["prices"], cd[c]["market_caps"]): # Iterate over both the prices and market_caps keys in parallel
                            writer.writerow([c, p[0], p[1], m[1]]) # coin, date, price, market cap
        

    def all_operations(self):
        """Function will do everything in one sequence; Get historical data, parse it monthly and put it in a file"""
        self.get_historical_data() # Get historical data
        self.parse_data_monthly() # Parse the monthly data

        if self.output_csv: # If output_csv is set to True
            self.export_to_csv() # Export our data to CSV

    def get_historical_data(self):
        """ Gets historical data from CoinGecko and puts grouped data in a file
        """
        d = dict() # Will store all of our data semi-organized in this dict and then put it in CoinDaata.json
        with open("CoinData.json", "r+") as f: # Open CoinData file
            for c in self.coin_list: # Iterate over coin_list
                d[c] = cg.get_coin_market_chart_by_id(c, self.vs_currency, self.date_to_days()) # Create a key in the dict with the coins name and have the value be the coingecko response
            json.dump(d, f) # Put our dictionary into the CoinData.json file

    def date_to_days(self):
        """ Returns how many days have gone by between historical date and today
        :return: The amount of days
        :rtype: int
        """
        past = datetime.strptime(self.date, "%d/%m/%Y") # Convert the date from above into a datetime object
        now = datetime.today() # Get todays date
        return (now - past).days

    def parse_data_monthly(self):
        """Takes the CoinData and parses each months' data for each coin's price + marketcap and puts it in a new file CoinData Exported 
        """
        dc = dict() # Create dict
        with open("CoinData.json", "r") as f: # Open CoinData.json
            d = json.load(f) # Load the file above as a dict
            for k in d: # Iterate over first set of json keys

                # Unparsed json file
                prices = d[k]["prices"] # Gets list of all the prices [unix timestamp, price]
                mc = d[k]["market_caps"] # Gets list of all market caps [unix timestamp, marketcap]

                # Parsing json file
                dc.update({k: {}}) # Prevent a KeyError by first making an empty object for each coin (so we're then able to do dict>coin>price/marketcap )
                dc[k]["prices"] = self.parse_keys_date(prices) # New dictionary[key(coin name)] prices key = parse_keys_date() of old dict
                dc[k]["market_caps"] = self.parse_keys_date(mc) # New dictionary[key(coin name)] market_caps key = parse_keys_date() of old dict

        with open("CoinData-Exported.json", "r+") as fe: # r+ because w+ instantly clears the file on open
            json.dump(dc, fe) # Dump dict into json file

    def parse_keys_date(self, key: list):
        """Parse the arrays from the given keys and returns the list (only monthly data)
        :param list: key List with [unix timestamp, price/mcap]
        :return: List of [date, price/mcap]
        :rtype list:
        """
        r = list() # Create list which will be used for our data [[date, price], [date, price]]
        for v in key: # Iterate over key parameter
            d = self.is_first_of_month(v[0]) # Call is_first_of_month function on the timestamp format
            if d[0]: # If is_first_of_month is true 
                r.append([d[1].strftime("%d/%m/%Y"), v[1]]) # Add [parsed date, price] to our r list
        return r
                
    def is_first_of_month(self, timestamp):
        """Returns boolean wether the timestamp is the first of the month, if true will also return the month
        :param: Unix timestamp
        :return: Bool if timestamp is first of month
        :rtype: boolean
        :return: date
        :rtype: datetime.date
        """
        date = datetime.utcfromtimestamp(timestamp / 1000) # Convert timestamp to actual datetime object (divided by 1000 for ms -> s)

        if date.day == 1: # If the day is number 1 (new month)
            return True, date # Return true(new month), date of the month

        return False, "" # Not new month


c = Coin("usd", "01/06/2020")
c.all_operations()