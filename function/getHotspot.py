import requests
from datetime import datetime, timedelta

headers = {
            "Content-Type": "application/json"
            }
    
    
url = 'http://127.0.0.1:9000/api/addhotspot/'
data = requests.get('https://hotspot.brin.go.id/getHS?$$hashKey=object:32&class=hotspot&conf_lvl=low&enddate=&id=0&loc={"stt":"Indonesia","disp":"Indonesia"}&mode=cluster&name=Hotspot&startdate=&time=last24h&visibility=true', headers=headers)
data = data.json()
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
    respnse = requests.post(url, json=detail, headers=headers)
    print("LAPAN :", respnse.json())

siponi_url = 'https://sipongi.menlhk.go.id/api/opsroom/indoHotspot?wilayah=IN&filterperiode=false&late=24&satelit[]=NASA-MODIS&satelit[]=NASA-SNPP&satelit[]=NASA-NOAA20&confidence[]=high&confidence[]=medium&confidence[]=low'
data = requests.get(siponi_url)
data = data.json()
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

    respnse = requests.post(url, json=detail, headers=headers)
    #print(detail)
    print("Sipongi :", respnse.json())