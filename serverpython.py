from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import json, requests, urllib
from bs4 import BeautifulSoup

app = Flask(__name__)
api = Api(app)

api_key = "95aCMpBNiNhpldzn8tHqBQv3B1YDUpac"
weather_api = "18606e8835f63574b40bc45d4a52198c"

def get_weather(state):
    
    res = requests.get("http://api.openweathermap.org/data/2.5/weather?APPID="+weather_api+"&q="+state)
    result = res.json()
    data = result["weather"]
    w_data = data[0]

    loc = result["main"]
    temp = loc["temp"]
    desc = w_data["description"]
    return {"data" : [{"description" : desc},{"temperature" : str(float(temp)-273)}]}

def get_room_pics(hotel_name, city):
    
    hotel_name = str(hotel_name)
    hotel_name = hotel_name.replace(" ", "+")
    res = requests.get("http://www.bing.com/images/search?q="+hotel_name+"+"+city+"+rooms+jpg&FORM=HDRSC2")
    soup = BeautifulSoup(res.text, "html.parser")

    a_tags = soup.findAll("a")
    z = 0
    links = []
    for i in range(len(a_tags)):
        link = str(a_tags[i].attrs["href"])
        if(len(link) > 10):
            if(link[0:4] == "http" and link[len(link)-4 : len(link)] == ".jpg"):
                links.append(link)
                z += 1
                if(z == 10):
                    break
    return links

def get_hotel_data(city):

    url = "http://terminal2.expedia.com/x/mhotels/search?city="+str(city)+"&resultsPerPage=5&sortOrder=true&checkInDate=2016-12-01&checkOutDate=2016-12-03&room1=2&apikey="+api_key
    res = requests.get(url)
    dictionary = [{}]
    result = res.json()
    List = result["hotelList"]
    final_json = {}

    for hotel in List:
        try:
            name = hotel["localizedName"]
            rating = hotel["hotelStarRating"]
            desc = hotel["shortDescription"]
            loc_desc = hotel["locationDescription"]
            thumb = hotel["largeThumbnailUrl"]
            thumb = "https://media.expedia.com"+thumb
            img_links = get_room_pics(name, city)

            y = {}
            y.update({"name" : name})
            y.update({"rating" : rating})
            y.update({"description" : desc})
            y.update({"location_description" : loc_desc})
            y.update({"thumbnail" : thumb})
            y.update({"images" : img_links})
            dictionary.append(y)
        except:
            pass

    dictionary.pop(0)
    final_json.update({"hotelList" : dictionary})
    return final_json

class Data_Miner1(Resource):

    def get(self, city):
        return get_hotel_data(city)

class Data_Miner2(Resource):

    def get(self, state):
        return get_weather(state)

api.add_resource(Data_Miner1, '/data1/<string:city>')
api.add_resource(Data_Miner2, '/data2/<string:state>')

if(__name__ == '__main__'):
    app.run(host="192.168.43.23", port="7000")
