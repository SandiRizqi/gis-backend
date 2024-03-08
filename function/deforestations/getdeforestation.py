import rasterio
from rasterio.features import shapes
import numpy as np
from sqlalchemy import create_engine
import geopandas as gpd
import requests
import rasterio.mask
from datetime import timedelta, date
import requests
import json
import threading
from rest_framework.parsers import JSONParser
from api.models import DEFORESTATIONS_EVENTS_ALERT_LIST, PALMS_COMPANY_LIST
from django.http import JsonResponse, HttpResponse
from django.contrib.gis.geos import GEOSGeometry



def getjson(path):
    with open(path, 'r') as f:
        d = json.load(f)
    return d



def getdate(number):
    #conf = int(str(number)[0])
    day = int(str(number)[1:])
    start_data = date(2014,12,31)
    end_date = start_data+ timedelta(days=day)
    return str(end_date)

def getconf(number):
    conf = int(str(number)[0])
    return conf

def get_tiles(db_connection_url):
    dbengine = create_engine(db_connection_url)
    sql = "SELECT * FROM api_palms_company_list"
    estate = gpd.read_postgis(sql, con=dbengine).to_crs('epsg:4326')
    estate['CREATED'] = estate['CREATED'].astype(str)
    estate['UPDATED'] = estate['UPDATED'].astype(str)
    zone = gpd.read_file('./vectors/zones/Integrated_deforestation_alerts.shp').to_crs('epsg:4326')
    estate = estate.overlay(zone, how='intersection')
    tiles_id = estate['tile_id'].unique()
    for tile in tiles_id:
        read_img(tile)
    estate = json.loads(estate.to_json())
    #threads = []
    for ft in estate['features']:
        get_data(ft, ft['properties']['tile_id'], ft['properties']['COMP_NAME'], ft['properties']['id'])
        #thread = threading.Thread(target=get_data, args=(ft, ft['properties']['tile_id'], ft['properties']['COMP_NAME'], ft['properties']['id']))

    return True


def rasterio_clip(feature, tile_id, name):
    shapes = [feature["geometry"]]

    for i, shape in enumerate(shapes):
        with rasterio.Env():
            with rasterio.open("./tiles/{}.tif".format(tile_id)) as src:
                out_image, out_transform = rasterio.mask.mask(src, [shape], crop=True)
                out_meta = src.meta

            out_meta.update({"driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform})

            with rasterio.open("./temp/temp-{}.tif".format(name), "w", **out_meta) as dest:
                dest.write(out_image)

def read_img(tile_id):
    url = "https://data-api.globalforestwatch.org/dataset/gfw_integrated_alerts/latest/download/geotiff?grid=10/100000&tile_id={}&pixel_meaning=date_conf&x-api-key=2d60cd88-8348-4c0f-a6d5-bd9adb585a8c".format(tile_id)
    response = requests.get(url)
    open("./tiles/{}.tif".format(tile_id), "wb").write(response.content)

def get_vector(name, id):
     with rasterio.Env():
        with rasterio.open("./temp/temp-{}.tif".format(id), 'r') as src:
            mask = 0
            arr = src.read(1)
            is_valid = (arr != mask).astype(np.uint8)
            #results = ({'properties': {'value': int(v),'comp_name': name, 'comp_id': id}, 'geometry': s}for i, (s, v) in enumerate(shapes(arr, mask=is_valid, connectivity=4, transform=src.transform)))
            geoms = []
            for _, (s, v) in enumerate(shapes(arr, mask=is_valid, connectivity=4, transform=src.transform)):
                
                if s['type'] == "Polygon":
                    coord = [list(s['coordinates'])]
                else:
                    coord = list(s['coordinates'])

                row = {
                    'type': 'Feature',
                    'properties': {'value': int(v),
                                      'comp_name': name,
                                      'comp_id': id},
                        'geometry': {
                                    'type': 'MultiPolygon',
                                    'coordinates': coord
                                      }}
                geoms.append(row)
            #geoms = list(results)
            features = {
                "type": "FeatureCollection",
                "features": geoms
                }
            
            if len(features['features']) > 0:
                print(features)
                gdb = gpd.GeoDataFrame.from_features(features)
                gdb = gdb.set_geometry('geometry', crs='EPSG:4326')
                gdb['dates'] = gdb.apply(lambda row: getdate(int(row.value)), axis=1)
                gdb['conf'] = gdb.apply(lambda row: getconf(int(row.value)), axis=1)
                gdb = gdb.dissolve(by=['dates', 'comp_name', 'comp_id'])
                gdb = gdb.sort_values(by=['dates'])
                gdb = gdb.to_crs('epsg:3857')
                gdb['hectares'] = gdb['geometry'].area/10**4
                gdb = gdb.to_crs('epsg:4326')
                gdb.to_file("./vectors/alerts/{}.json".format(id), driver="GeoJSON")
            else:
                print("No alert")

        return True

        
def get_data(shapefile_pt, tile_id, name, id):
    
        #read_img(tile_id)
    print("Processing, ", name)
    rasterio_clip(shapefile_pt, tile_id, id)
    get_vector(name, id)

   


def postData(host, token, url, name):
    print("Post data", name)
    geojson =  getjson(url)
    for data in geojson['features']:
        if data['geometry']['type'] == "Polygon":
            geom = {
            "type": "MultiPolygon",
            "coordinates": [data['geometry']['coordinates']]
            }
        else:
            geom = {
            "type": "MultiPolygon",
            "coordinates": data['geometry']['coordinates']
            }
        post = {
            "id": data['properties']['comp_id'],
            "event_id": "{}/{}".format(data['properties']['comp_id'], data['properties']['dates']),
            "alert_date":data['properties']['dates'],
            "area": float(data['properties']['hectares']),
            "geometry": geom

        }
        header = {
            "Content-Type" : "application/json",
            "Authorization": f"Token {token}"
        }
        ress = requests.post(f'{host}/api/adddeforestations/', json=json.loads(json.dumps(post)), headers=header)
        print(ress.status_code)


def UpdateDatabase(url, name):
    print("Post data", name)
    geojson =  getjson(url)
    for data in geojson['features']:
        if data['geometry']['type'] == "Polygon":
            geom = {
            "type": "MultiPolygon",
            "coordinates": [data['geometry']['coordinates']]
            }
        else:
            geom = {
            "type": "MultiPolygon",
            "coordinates": data['geometry']['coordinates']
            }
        post = {
            "id": data['properties']['comp_id'],
            "event_id": "{}/{}".format(data['properties']['comp_id'], data['properties']['dates']),
            "alert_date":data['properties']['dates'],
            "area": float(data['properties']['hectares']),
            "geometry": geom

        }

        df = post
        comp_id = df['id']
        COMP = PALMS_COMPANY_LIST.objects.get(id=int(comp_id))
        EVENT_ID=df['event_id']
        AREA=df['area']
        ALERT_DATE=df['alert_date']
        geometry = df['geometry']
        geom = GEOSGeometry(json.dumps(geometry))
        if not DEFORESTATIONS_EVENTS_ALERT_LIST.objects.filter(EVENT_ID=EVENT_ID).exists():
            DEFORESTATIONS_EVENTS_ALERT_LIST.objects.create(COMP=COMP, EVENT_ID=EVENT_ID, AREA=AREA, ALERT_DATE=ALERT_DATE, geom=geom)
            print("Add new data")
            #return JsonResponse({"message": "Added Successfully" })
        else:
            Event = DEFORESTATIONS_EVENTS_ALERT_LIST.objects.get(EVENT_ID=EVENT_ID)
            Event.AREA = AREA
            Event.geom = geom
            Event.save()
            print("Update data")
            #return JsonResponse({"message": "Data already Exist Updated" })
        
    