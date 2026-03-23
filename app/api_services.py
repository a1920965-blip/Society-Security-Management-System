import requests
import os
import pprint
def weather_api(city):
    request_url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={os.getenv('API_KEY')}"
    data=requests.get(request_url).json()
    print(data)
    context={"temp":data['main']['temp'],
            "weather_desc":data['weather'][0]['description'],
            'city':data['name'],
            'country':data['sys']['country'],
            'humidity':data['main']['humidity'],
            'wind_speed':data['wind']['speed']}
    return context