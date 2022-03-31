from bs4 import BeautifulSoup as bs
import requests

#Google doesn't have its own weather API, it also scrapes from weather.com

#Google tries to prevent us from scraping its website programmatically, 
#need to pretend I'm a legit web browser by defining a user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
#US English
LANGUAGE = "en-US,en;q=0.5"

#function that given a URL, extracts all useful weather info
#return info in a dict
def get_weather_data(url):
    #create a session w/ browser & language 
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html = session.get(url) #download HTML code from web
    #create new BeautifulSoup object with an HTML parser
    soup = bs(html.text, "html.parser")

    #grab HTML info, use soup.find() to specify the HTML tag name and matched attributes
    #EX: div element with an id gets us location

    #store all results in a dict
    result = {}
    #extract region
    result['region'] = soup.find("div", attrs={"id": "wob_loc"}).text
    #extract current temp 
    result['temp_now'] = soup.find("span", attrs={"id": "wob_tm"}).text
    #get current day and hour
    result['dayhour'] = soup.find("div", attrs={"id": "wob_dts"}).text
    #get actual weather
    result['weather_now'] = soup.find("span", attrs={"id": "wob_dc"}).text
    
    #get precip
    result['precipitation'] = soup.find("span", attrs={"id": "wob_pp"}).text
    #get % of humidity
    result['humidity'] = soup.find("span", attrs={"id": "wob_hm"}).text
    #extract the wind
    result['wind'] = soup.find("span", attrs={"id": "wob_ws"}).text

    #get next couple days weather
    #first child of div element of class Z1VzSb in aria-label attribute
    #within alt attribute and img element
    next_days = []
    days = soup.find("div", attrs={"id": "wob_dp"})

    for day in days.findAll("div", attrs={"class": "wob_df"}):
        #extract name of the day
        day_name = day.findAll("div")[0].attrs['aria-label']
        #get weather status for that day
        weather = day.find("img").attrs["alt"]
        temp = day.findAll("span", {"class": "wob_t"})
        #max temp in F
        max_temp = temp[0].text
        #min temp in F
        min_temp = temp[2].text
        next_days.append({"name": day_name, "weather": weather, "max_temp": max_temp, "min_temp": min_temp})

    #append to result
    result['next_days'] = next_days

    #result dict got everything we need 
    return result

#parse command-line arguments
if __name__ == "__main__":
    URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather"
    import argparse
    parser = argparse.ArgumentParser(description="Script for Extracting Weather Data using Google Weather")
    parser.add_argument("region", nargs="?", help="""Region to get weather for, must be available region. Default is your current location determined by your IP Address""", default="")

    #parse arguments
    args = parser.parse_args()
    region = args.region
    URL += region
    #get data 
    data = get_weather_data(URL)

#DISPLAYING THE DATA    
print("Weather for:", data["region"])
print("Currently:", data["dayhour"])
print("Current Temperature in Fahrenheit:", data["temp_now"])
print("Description:", data['weather_now'])
print("Precipitation:", data["precipitation"])
print("Humidity:", data["humidity"])
print("Wind:", data["wind"])
print("Next days:")
for dayweather in data["next_days"]:
    print("="*40, dayweather["name"], "="*40)
    print("Description:", dayweather["weather"])
    print("Max Temperature(F):", dayweather["max_temp"])
    print("Min Temperature(F):", dayweather["min_temp"])
    #print(f"Minimum Temperature: {dayweather['min_temp']} F")


