# KayakScraper

## Overview
This Kayak scraper is a Python tool designed to scrape flight information from Kayak.com, including airline, flight timings, and pricing details. It enhances decision-making by integrating real-time weather data from OpenWeatherMap to allow users to understand flight circumstances. Given a range of time, the program is also able to query and find the cheapest flight.

## Features
- **Flight Data Extraction**: Scrapes flight data such as airline names, timings, and prices from Kayak through Selenium and BeautifulSoup Also return cheapest flight in a range query.
- **Weather Integration**: Fetches and displays weather information for the departure city using the OpenWeatherMap API.
- **Local Storage**: Saves all flight and weather data in a SQLite database for offline access and further analysis. Also utilzes the Pony ORM.

### Prerequisites
- Python 3.8+
- Google Chrome Browser
- ChromeDriver compatible with the installed Chrome version
- Conda for Virtual Environment

### Setup Instructions
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/KayakScraper.git
   cd KayakScraper

## Installation
1.Install dependencies using:
    pip install -r requirements.txt

2.Obtain API Key
    - Obtain a free API key from OpenWeatherMap.
    - Set the API key in a JSON file
    -Open JSON file in read mode