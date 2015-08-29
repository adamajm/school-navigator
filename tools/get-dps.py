import sys
import json
import requests

def step1(address):
    url = 'http://gisweb2.durhamnc.gov/ArcGIS/rest/services/SharedMaps/Parcels/MapServer/3/query'
    params = {
        'outFields': "PARCEL_ID,PIN,OWNER_NAME,OWNER_ADDR,SITE_ADDRE",
        'returnGeometry': "true",
        'spatialRel': "esriSpatialRelIntersects",
        'f': "json",
        'where': "SITE_ADDRE LIKE '{}%'".format(address),
        'returnDistinctValues': "false",
    }
    r = requests.get(url, params=params)
    if len(r.json()['features']) == 0:
        raise Exception('Address entered: "{}" not found'.format(address))
    return r.json()

def step2(rings):
    url = 'http://gisweb2.durhamnc.gov/ArcGIS/rest/services/CoreTasks/Geometry/GeometryServer/labelPoints'
    params = {
        'polygons': '[{"rings":' + repr(rings) + '}]',
        'sr' :"102719",
        'f': "json",
    }
    r = requests.post(url, data=params)
    return r.json()

def step3(geolocation):
    url = 'http://gisweb2.durhamnc.gov/arcgis/rest/services/DurhamMaps/DPS_Schools_test/MapServer/identify'
    params = {
        'geometry': repr(geolocation),
        'layers': 'all:1,2,3,4,5,6,7,8',
        'tolerance': '0',
        'mapExtent': '1878717.4182397667,767235.8877083337,2199711.8626842108,935757.9710416669',
        'imageDisplay': '1280,672,96',
        'f': 'json',
        'returnGeometry': 'false',
    }
    r = requests.get(url, params=params)
    return r.json()

if __name__ == '__main__':
    address = ' '.join(sys.argv[1:])
    print(address)
    
    parcel = step1(address)
    #print(json.dumps(parcel, indent=2))
    addr = parcel['features'][0]['attributes']['SITE_ADDRE'].strip()
    rings = parcel['features'][0]['geometry']['rings']
    print(addr)

    location = step2(rings)
    #print(json.dumps(location, indent=2))
    geolocation = location['labelPoints'][0]
    print(geolocation)
    
    schools = step3(geolocation)
    #print(json.dumps(schools, indent=2))

    for result in schools['results']:
        id = result['layerId']
        type = result['layerName']
        name = result['value']
        print(id, type, ':', name)
