from celery import shared_task
from sqlalchemy import text
import requests
import json
from glob import glob
import os
from gisbackend.settings import env
from function.hotspots.update import getNear
from function.hotspots.utils import inactive_hotspot
from function.deforestations.getdeforestation import *
from datetime import datetime, timedelta, date


@shared_task(bind=True)
def add_hotspot(self):
    webhost = env.get('WEB_HOST')
    headers = {
            "Content-Type": "application/json"
            }
    
    post_url = f"{webhost}/api/addhotspot/"
    data = requests.get('https://hotspot.brin.go.id/getHS?$$hashKey=object:32&class=hotspot&conf_lvl=low&enddate=&id=0&loc={"stt":"Indonesia","disp":"Indonesia"}&mode=cluster&name=Hotspot&startdate=&time=last24h&visibility=true', headers=headers)
    data = data.json()

    if len(data['features']) > 0:
        for feature in data['features']:
            detail = requests.get('https://hotspot.brin.go.id/getHSdetail?hsid={}&mode=cluster'.format(feature['id']), headers=headers)
            detail = detail.json()
            detail['geometry'] = feature['geometry']
            detail['radius'] = feature['properties']['r']
            detail['source'] = "LAPAN"
            detail['long'] = float(feature['geometry']['coordinates'][0])
            detail['lat'] = float(feature['geometry']['coordinates'][1])
            detail['provinsi'] = str(detail['loc']).split(", ")[0]
            detail['kabupaten'] = str(detail['loc']).split(", ")[1]
            detail['kecamatan'] = str(detail['loc']).split(", ")[2]
            detail['date'] = str(detail['time']).split()[0]
            detail['times'] = str(detail['time']).split()[1]
            respnse = requests.post(post_url, json=detail, headers=headers)
            print("LAPAN :", respnse.status_code)

    siponi_url = 'https://sipongi.menlhk.go.id/api/opsroom/indoHotspot?wilayah=IN&filterperiode=false&late=24&satelit[]=NASA-MODIS&satelit[]=NASA-SNPP&satelit[]=NASA-NOAA20&confidence[]=high&confidence[]=medium&confidence[]=low'
    data = requests.get(siponi_url)
    data = data.json()
    if len(data['features']) > 0:
        for feature in data['features']:
            detail = {}
            conf = str(feature['properties']['confidence_level']).upper()
            label = str(feature['properties']['date_hotspot_ori'])
            date = datetime.strptime(label, '%Y-%m-%dT%H:%M:%S.%f%z')
            hotspottime = date + timedelta(hours=7)

            detail['conf'] = 7
            if conf == "HIGH":
                detail['conf'] = 9
            elif conf == "MEDIUM":
                detail['conf'] = 8
            
            detail['geometry'] = feature['geometry']
            detail['radius'] = 0
            detail['source'] = "SIPONGI"
            detail['long'] = float(feature['geometry']['coordinates'][0])
            detail['lat'] = float(feature['geometry']['coordinates'][1])
            detail['id'] = '{}/{}'.format("SPG", str(feature['properties']['hs_id']))
            detail['provinsi'] = str(feature['properties']['nama_provinsi'])
            detail['kabupaten'] = str(feature['properties']['kabkota'])
            detail['kecamatan'] = str(feature['properties']['kecamatan'])
            detail['date'] = str(hotspottime).split(" ")[0]
            detail['times'] = str(hotspottime).split(" ")[1]
            #detail['conf'] = str(feature['properties']['confidence_level']).upper()
            detail['sat'] = str(feature['properties']['sumber']).upper()

            respnse = requests.post(post_url, json=detail, headers=headers)
            #print(detail)
            print("Sipongi :", respnse.status_code)

    return "Add Hotspot Data Done"


#@shared_task(bind=True)
def update_deforestations():
    dbhost = env.get('DB_HOST')
    database = env.get('DB_NAME')
    user = env.get('DB_USER')
    password = env.get('DB_PASSWORD')
    port = env.get('DB_PORT')
    #webhost = env.get('WEB_HOST')
    #token = env.get('TOKEN')
    db_connection_url = f"postgresql://{user}:{password}@{dbhost}:{str(port)}/{database}"
    tiles = get_tiles(db_connection_url)
    if tiles:
        files = [os.path.basename(x) for x in glob('./vectors/alerts/*.geojson')]
        for file in files:
            UpdateDatabase('./vectors/alerts/' + file, file)
            #postData(webhost, token, './vectors/alerts/' + file, file)
        files = glob('./vectors/alerts/*')
        for items in files:
            os.remove(items)
        return "Update Deforestation Data Done"
    else:
        return "Failed to Update Deforestation Data"


@shared_task(bind=True)
def update_hotspots(self):
    MODE = env.get('MODE')
    dbhost = env.get('DB_HOST')
    database = env.get('DB_NAME')
    user = env.get('DB_USER')
    password = env.get('DB_PASSWORD')
    port = env.get('DB_PORT')
    db_connection_url = f"postgresql://{user}:{password}@{dbhost}:{str(port)}/{database}"
    webhost = env.get('WEB_HOST')
    token = env.get('TOKEN')
    #print(token)

    today = date.today()
    
    
    con = create_engine(db_connection_url)
    table = "api_palms_company_list"
    sql = "SELECT * FROM \"{}\"".format(table)
    polygons = gpd.GeoDataFrame.from_postgis(text(sql), con, geom_col='geom').to_crs("+proj=utm +zone=50 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

    point = requests.get(webhost + '/api/hotspot/?conf=0&startdate={}&enddate={}'.format(today, today))
    point = json.dumps(point.json())
    point = gpd.read_file(point).to_crs("+proj=utm +zone=50 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

    getNear(point, polygons, webhost, token)
    return f"Hotspot Updated :{MODE}"


@shared_task(bind=True)
def deactivate_hotspots(self):
    today = str(date.today())
    query = "UPDATE {} SET {} = {} WHERE \"STATUS\" = {}".format('"api_fire_events_alert_list"', '"STATUS"' , "'INACTIVE'", "'ACTIVE'")
    dbhost = env.get('DB_HOST')
    database = env.get('DB_NAME')
    user = env.get('DB_USER')
    password = env.get('DB_PASSWORD')
    port = int(env.get('DB_PORT'))
    
    inactive_hotspot(dbhost, database, user, password, port, query)

    return f"Hotspot deactivated"