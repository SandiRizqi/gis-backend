import requests


def getHotspot():
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
        detail['provinsi'] = str(detail['loc']).split(", ")[0]
        detail['kabupaten'] = str(detail['loc']).split(", ")[1]
        detail['kecamatan'] = str(detail['loc']).split(", ")[2]
        detail['date'] = str(detail['time']).split()[0]
        detail['times'] = str(detail['time']).split()[1]
        respnse = requests.post(url, json=detail, headers=headers)
        print(respnse.status_code)