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
import json


db = orm.Database()
orm.set_sql_debug(True)
#create classes for db
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

    

###scraping functions

#scrape data from kayak
def get_kayak_data(from_location, to_location, start, end):
    url = f'https://www.kayak.com/flights/{from_location}-{to_location}/{start}/{end}?sort=bestflight_a'
    driver = webdriver.Chrome()
    driver.get(url)
    sleep(10)
    flight_rows = driver.find_elements('xpath', '//div[@class="nrc6-wrapper"]')
    return flight_rows

#parse scraped data and fill arrays
def parse_data(flight_rows):
    flights_data = []
    for WebElement in flight_rows:
        elementHTML = WebElement.get_attribute('outerHTML')
        elementSoup = BeautifulSoup(elementHTML, 'html.parser')

        # Get prices
        temp_price = elementSoup.find("div", {"class": "nrc6-price-section nrc6-mod-multi-fare"})
        price = temp_price.find("div", {"class": "f8F1-price-text"})
        price_text = price.text if price else "No price available"

        # Get airline names
        airline_names = elementSoup.find("div", {"class": "c_cgF c_cgF-mod-variant-default"}).text

        # Get times
        times = elementSoup.find("div", {"class": "vmXl vmXl-mod-variant-large"}).text

        flights_data.append({'airline': airline_names, 'price': price_text, 'time': times})
        
    return flights_data

#for privating api_key
#load your own api key into json file named config_json
def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config

#get weather data
def get_weather_data(start):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city = start

    config = load_config()
    api_key = config['OPENWEATHER_API_KEY']

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

#conversion function
def kelvin_to_fahrenheit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return fahrenheit

#data filtering to take range of time
def filter_flights_by_time(flights_data, start_time, end_time):
    filtered_flights = []
    start_time = datetime.strptime(start_time, '%I:%M %p').time()
    end_time = datetime.strptime(end_time, '%I:%M %p').time()

    for flight in flights_data:
        flight_start_time_str = flight['time'].split(' – ')[0].strip()
        try:
            flight_start_time = datetime.strptime(flight_start_time_str, '%I:%M %p').time()
            if start_time <= flight_start_time <= end_time:
                filtered_flights.append(flight)
        except ValueError as e:
            print("Error", e)
    return filtered_flights

#find cheapest flight
def find_cheapest_flight(filtered_flights):
    if not filtered_flights:
        print("No flights available in time range")
        return None

    cheapest_flight = min(filtered_flights, key=lambda x: float(x['price'].strip('$').replace(',', '')))

    print(f"Cheapest Flight: {cheapest_flight['airline']} at {cheapest_flight['time']} for {cheapest_flight['price']}")
    return cheapest_flight

#main
def main():
    from_location = 'CHI'
    to_location = 'MIA'
    start = '2024-09-01'   #enter date in year-month-day format, for example september 1, 2024 would be 2024-09-1
    end = '2024-09-08'     #enter date in year-month-day format, for example september 1, 2024 would be 2024-09-1

    query_start = '12:00 PM' #query by flight start time
    query_end = '11:00 PM'
    
    initialize_database()
    flight_rows = get_kayak_data(from_location, to_location, start, end)
    flights_data = parse_data(flight_rows)

    add_data([f['airline'] for f in flights_data], [f['price'] for f in flights_data], [f['time'] for f in flights_data])
    
    get_weather_data(from_location)
    get_weather_data(to_location)
    filtered_flights = filter_flights_by_time(flights_data, query_start, query_end)
    find_cheapest_flight(filtered_flights)

if __name__ == "__main__":
    main()