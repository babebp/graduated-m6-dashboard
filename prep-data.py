import pandas as pd
import requests
import json

def eng2thai_province(geojson, data):

    province_dict = {"Songkhla (Songkhla Lake)": "สงขลา", "Phatthalung (Songkhla Lake)": 'พัทลุง', "Lop Buri": "ลพบุรี", "Bangkok Metropolis": "กรุงเทพมหานคร"}

    for i in data:
        province_dict[i['name_en']] =  i['name_th']
    
    
    for i in geojson['features']:
        try:
            en_province = i['properties']['NAME_1']
            i['properties']['NAME_1'] = province_dict[en_province]
        except:
            pass

    return geojson

# def map_id_province(geojson, data):
#     id_dict = {}
#     for i in geojson['features']:
#         id_dict[i['properties']['NAME_1']] = i['properties']["ID_1"]

#     # 'totalmale': '340', 'totalfemale': '633', 'totalstd': '973'
#     df = pd.DataFrame(data)

#     df['schools_province'].apply(lambda x: id_dict[x])

#     print(df)
#     # print(id_dict)


if __name__ == "__main__":
    with open('thailand-provinces.geojson') as f:
        geojson = json.load(f)
    
    data = requests.get("https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_province.json").json()

    new_geojson = eng2thai_province(geojson, data)

    # print(new_geojson['features'][0]['properties'])

    # with open("prep-thailand-provinces.geojson", "w", encoding="utf-8") as f:
    #     json.dump(new_geojson, f, ensure_ascii=False, indent=4)


    # data = requests.get("https://gpa.obec.go.th/reportdata/pp3-4_2566_province.json").json()

    # df = pd.DataFrame(data)

    # df = df[["schools_province", "totalmale", "totalfemale", "totalstd"]]
    # print(df)

    # with open('thailand-provinces.geojson') as f:
    #     geojson = json.load(f)
    
    # map_id_province(new_geojson, data)
    