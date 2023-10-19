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
import datetime



@shared_task(bind=True)
def update_deforestations(self):
    dbhost = env.get('DB_HOST')
    database = env.get('DB_NAME')
    user = env.get('DB_USER')
    password = env.get('DB_PASSWORD')
    port = env.get('DB_PORT')
    webhost = env.get('WEB_HOST')
    token = env.get('TOKEN')
    db_connection_url = f"postgresql://{user}:{password}@{dbhost}:{str(port)}/{database}"
    tiles = get_tiles(db_connection_url)
    if tiles:
        files = [os.path.basename(x) for x in glob('./vectors/alerts/*.geojson')]
        threads = []
        for file in files:
            thread = threading.Thread(target=postData, args=(webhost, token, './vectors/alerts/' + file, file))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
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

    today = datetime.date.today()
    
    
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
    date = str(datetime.date.today())
    query = "UPDATE {} SET {} = {} WHERE \"EVENT_DATE\" <> '{}'::DATE".format('"api_fire_events_alert_list"', '"STATUS"' , "'INACTIVE'", date)
    dbhost = env.get('DB_HOST')
    database = env.get('DB_NAME')
    user = env.get('DB_USER')
    password = env.get('DB_PASSWORD')
    port = int(env.get('DB_PORT'))
    
    inactive_hotspot(dbhost, database, user, password, port, query)

    return f"Hotspot deactivated"