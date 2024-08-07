import pandas as pd
#scraper imports
from time import sleep
from selenium import webdriver #using selenium to get the HTML
from bs4 import BeautifulSoup #using beautifulsoup to extract whatever we need from HTML
#database imports
from pony import orm
from datetime import datetime
#weather api
import requests

import os
import csv


db = orm.Database()
orm.set_sql_debug(True)

class Item(db.Entity):
    prices = orm.Set("Price")
    airlines = orm.Required(str)
    timings = orm.Optional(str)

class Price(db.Entity):
    item = orm.Required(Item)
    date_created = orm.Required(datetime)
    value = orm.Required(str)

#database init
def initialize_database():
    db.bind(provider="sqlite", filename="kayakscraper.db", create_db=True)
    db.generate_mapping(create_tables=True)

#add data to database
def add_data(airlines, prices, times):
    try:
        with orm.db_session:
            for airline, price, time in zip(airlines, prices, times):
                new_item = Item(airlines = airline, timings = time)
                new_price = Price(item = new_item, date_created = datetime.now(), value = price)
    except orm.TransactionIntegrityError as err:
        print("Error: Item exists", err)

    

#scraping functions
def get_kayak_data(from_location, to_location, start, end):
    url = f'https://www.kayak.com/flights/{from_location}-{to_location}/{start}/{end}?sort=bestflight_a'
    driver = webdriver.Chrome()
    driver.get(url)
    sleep(10)
    flight_rows = driver.find_elements('xpath', '//div[@class="nrc6-wrapper"]')
    return flight_rows

def parse_data(flight_rows):
    lst_prices = []
    lst_airlines = []
    lst_time = []
    
    for WebElement in flight_rows:
        elementHTML = WebElement.get_attribute('outerHTML')
        elementSoup = BeautifulSoup(elementHTML, 'html.parser')

        #Get prices
        temp_price = elementSoup.find("div", {"class": "nrc6-price-section nrc6-mod-multi-fare"})
        price = temp_price.find("div", {"class": "f8F1-price-text"})
        if price:
            lst_prices.append(price.text)
        else:
            lst_prices.append("No price available")

        #Get airline names
        airline_names = elementSoup.find("div", {"class": "c_cgF c_cgF-mod-variant-default"}).text
        lst_airlines.append(airline_names)

        #Get times
        times = elementSoup.find("div", {"class": "vmXl vmXl-mod-variant-large"}).text
        lst_time.append(times)
        
    return lst_airlines, lst_prices, lst_time

#get weather data
def get_weather_data(start):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = '1c48db88097cd7f42530582d597c7b59'
    city = start

    url = base_url + "appid=" + api_key + "&q=" + city
    response = requests.get(url).json()
    #print (response)

    temp_kelvin = response['main']['temp']
    temp_fahrenheit = kelvin_to_fahrenheit(temp_kelvin)

    feels_like_kelvin = response['main']['feels_like']
    feels_like_fahrenheit = kelvin_to_fahrenheit(feels_like_kelvin)

    description = response['weather'][0]['description']
    

    print(f"The weather in {city} is: {description}")
    print(f"Temperature in {city}: {temp_fahrenheit} degrees Fahrenheit")
    print(f"Feels like Temperature in {city}: {feels_like_fahrenheit} degrees Fahrenheit")


def kelvin_to_fahrenheit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return fahrenheit


#main
def main():
    from_location = 'CHI'
    to_location = 'MIA'
    start = '2024-09-01'   #enter date in year-month-day format, for example september 1, 2024 would be 2024-09-1
    end = '2024-09-08'     #enter date in year-month-day format, for example september 1, 2024 would be 2024-09-1
    
    initialize_database()
    flight_rows = get_kayak_data(from_location, to_location, start, end)
    airlines, prices, times = parse_data(flight_rows)

    add_data(airlines, prices, times)
    
    print(airlines)
    print(prices)
    print(times)
    get_weather_data(from_location)
    get_weather_data(to_location)

if __name__ == "__main__":
    main()