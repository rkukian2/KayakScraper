import pandas as pd
from time import sleep
from selenium import webdriver #using selenium to get the HTML
from bs4 import BeautifulSoup #using beautifulsoup to extract whatever we need from HTML

import os #can help save data as csv file on computer

driver = webdriver.Chrome()
from_location = 'CHI'
to_location = 'MIA'
start = '2024-09-01' #enter date in year-month-day format, for example september 1, 2024 would be 2024-09-1
end = '2024-09-08'   #enter date in year-month-day format, for example september 1, 2024 would be 2024-09-1
url = 'https://www.kayak.com/flights/{from_location}-{to_location}/{start}/{end}?sort=bestflight_a'.format(to_location = to_location, from_location = from_location, start = start, end = end)
#not using keys, just a specific url to get the exact data we need




driver.get(url)
sleep(10)
flight_rows = driver.find_elements('xpath', '//div[@class="nrc6-wrapper"]')
#flight_rows = driver.find_elements_by_xpath('//*[@id="listWrapper"]/div/div[2]/div[2]/div[2]/div[2]/div/div')
print(flight_rows)

lst_prices = []
lst_airlines = []
lst_time = []

for WebElement in flight_rows:
    elementHTML = WebElement.get_attribute('outerHTML')
    elementSoup = BeautifulSoup(elementHTML, 'html.parser')

    #get prices
    temp_price = elementSoup.find("div", {"class": "nrc6-price-section nrc6-mod-multi-fare"})
    price = temp_price.find("div", {"class": "f8F1-price-text"})
    lst_prices.append(price.text)

    #get airline
    airline_names = elementSoup.find("div", {"class": "c_cgF c_cgF-mod-variant-default"}).text
    lst_airlines.append(airline_names)

    #get times
    times = elementSoup.find("div", {"class": "vmXl vmXl-mod-variant-large"}).text
    lst_time.append(times)
   

print(lst_airlines)
print(lst_prices)
print(lst_time)
