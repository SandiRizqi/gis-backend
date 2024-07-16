import geopandas as gpd
import requests
import sqlalchemy
import json
import os
from sqlalchemy import create_engine
from sqlalchemy import text
import datetime
#from utils import inactive_hotspot




def sendAlert(featurescollections, host, token):
    data = json.loads(featurescollections)
    if len(data['features']) > 0:
        for ft in data['features']:
            try:
                attr = ft['properties']
                post = {
                    'COMP' : int(attr['id']),
                    'COMP_NAME' : attr['COMP_NAME'],
                    'COMP_GROUP' : attr['COMP_GROUP'],
                    #'EVENT_ID' : str(attr['UID']),
                    'EVENT_DATE' : attr['DATE'],
                    'EVENT_TIME' : attr['TIME'],
                    'CONF' : int(attr['CONF']),
                    'SATELLITE' : attr['SATELLITE'],
                    'RADIUS' : int(attr['RADIUS']),
                    'KECAMATAN' : attr['KECAMATAN'],
                    'KEBUPATEN' : attr['KEBUPATEN'],
                    'PROVINSI' : attr['PROVINSI'],
                    'CATEGORY' : attr['CATEGORY'],
                    'LONG': round(ft['geometry']['coordinates'][0], 3),
                    'LAT': round(ft['geometry']['coordinates'][1], 3),
                    'distance' : float(attr['distance']),
                    'coordinates' : ft['geometry']['coordinates']
                }


                headers = {
                        "Content-Type": "application/json",
                        "Authorization" : f"Token {token}"
                }

                response = requests.post(host + '/api/events/fires/company/', data=json.dumps(post), headers=headers)
                response.raise_for_status()  
                print(response.json())
            except requests.exceptions.RequestException as e:
                print(f"Request failed with error:", e)
                continue


def addcat(row):
    dist = float(row['distance'])
    if dist > 5000:
        return "AMAN"
    if dist > 1000 and dist <= 5000:
        return "PERHATIAN"
    if dist > 0 and dist <= 1000:
        return "WASPADA"
    if dist <= 0:
        return "BAHAYA"

                                         

def getNear(point, polygons, host, token):
    print(point.head(5))
    print(len(point))
    print(polygons.head(5))

    near = gpd.sjoin_nearest(point, polygons, distance_col="distance", max_distance=20000).to_crs(4326)
    #print(len(near))

    near['CREATED'] = near['CREATED'].astype(str)
    near['UPDATED'] = near['UPDATED'].astype(str)
    near['CATEGORY'] = near.apply(lambda row: addcat(row), axis=1)
    data = near.to_json()

    if len(near) > 0:
        sendAlert(data, host, token)
    else:
        print("No data for update")
        pass

#getNear(point, polygons)
#inactive_hotspot(dbhost, database, user, password, port, query)

