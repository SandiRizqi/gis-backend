import geopandas as gpd
import requests
import json

from sqlalchemy import create_engine
from sqlalchemy import text
import datetime

today = datetime.date.today()

#host = 'https://backend.geo-circle.com/'
host = 'http://127.0.0.1:9000/'
token = 'Token 96188a88794241ebbd4c9594cb13fbc9f7b80dd2'

db_connection_url = "postgresql://tap_gis:T4pGreenGis88@postgresgis.tap-agri.com:5432/db_gis"
con = create_engine(db_connection_url)
table = "api_palms_company_list"
column = "COMP_GROUP"
value = "Triputra Group"
#sql = "SELECT * FROM \"{}\" WHERE \"{}\" = \'{}\'".format(table, column, value)
sql = "SELECT * FROM \"{}\"".format(table, column, value)
polygons = gpd.GeoDataFrame.from_postgis(text(sql), con, geom_col='geom').to_crs("+proj=utm +zone=50 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

point = requests.get(host + 'api/hotspot/?conf=0&startdate={}&enddate={}'.format(today, today))
point = json.dumps(point.json())
point = gpd.read_file(point).to_crs("+proj=utm +zone=50 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")


def sendAlert(featurescollections):
    data = json.loads(featurescollections)
    for ft in data['features']:
        try:
            attr = ft['properties']
            post = {
                'COMP' : int(attr['id']),
                'COMP_NAME' : attr['COMP_NAME'],
                'COMP_GROUP' : attr['COMP_GROUP'],
                'EVENT_ID' : int(attr['UID']),
                'EVENT_DATE' : attr['DATE'],
                'EVENT_TIME' : attr['TIME'],
                'CONF' : int(attr['CONF']),
                'SATELLITE' : attr['SATELLITE'],
                'RADIUS' : int(attr['RADIUS']),
                'KECAMATAN' : attr['KECAMATAN'],
                'KEBUPATEN' : attr['KEBUPATEN'],
                'PROVINSI' : attr['PROVINSI'],
                'CATEGORY' : attr['CATEGORY'],
                'distance' : float(attr['distance']),
                'coordinates' : ft['geometry']['coordinates']
            }


            headers = {
                    "Content-Type": "application/json",
                    "Authorization" : token
            }

            response = requests.post(host + 'api/hotspotevents/', data=json.dumps(post), headers=headers)
            response.raise_for_status()  
            print("Request succesfully")
        except requests.exceptions.RequestException:
            print(f"Request failed with error:")
            continue
        except requests.exceptions.ConnectionError:
            print(f"Request failed with error:")
            continue   # If there was an error, continue to the ne#print(post)
    print("Update Finished")


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

                                         

def getNear(pnt, pol):
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
        sendAlert(data)
    else:
        print("No data for update")
        pass

    #near.to_file('Nearest.geojson', driver='GeoJSON')  

    #polygons.to_file('Comp.geojson', driver='GeoJSON')  

    #point_gdf = gpd.GeoDataFrame(point, geometry='geometry')

    # Perform a spatial join between the Point GeoDataFrame and the Polygon FeatureCollection to find the nearest Polygon feature
    #joined = gpd.sjoin(point_gdf, polygons, op='nearest')

    # Extract the attributes of the nearest Polygon feature
    #nearest_feature = polygons.loc[joined.iloc[0]['index_right']]
    #distance = joined.iloc[0]['geometry'].distance(nearest_feature.geometry)
    #attribute1 = joined.iloc[0]['attribute1']
    #attribute2 = nearest_feature['attribute2']
    #print(f"Nearest distance = {distance}, attribute1 = {attribute1}, attribute2 = {attribute2}")

getNear(point, polygons)
