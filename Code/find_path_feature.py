import ast
import pandas as pd
import math
with open ("path_raw.txt", "r") as myfile:
    data = ast.literal_eval(myfile.read())

from math import radians,  cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

ty_list = [u'DUJUAN',
 u'NEPARTAK',
 u'SOUDELOR',
 u'HAGIBIS',
 u'NESAT',
 u'HAITANG',     
 u'FUNG-WONG',
 u'MEGI',
 u'MATMO',
 u'MERANTI',
 u'MALAKAS',
 u'CHAN-HOM']

path_df = pd.DataFrame(data)

df = pd.read_csv('df_1112.csv',encoding='utf8')
from datetime import datetime


## over distance
def find_strong_strength_double_(typhoon1,typhoon2,vil_lon,vil_lat,path_df):
    try:
        typhoon = typhoon1
        tmp_df = path_df.query("eName=='{}'".format(typhoon))
        tmp_df = pd.DataFrame(list(tmp_df['path'].values)[0])
        tmp_df['lon'] = tmp_df['lon'].astype(float)
        tmp_df['lat'] = tmp_df['lat'].astype(float)
        tmp_df['intensity'] = tmp_df['intensity'].astype(float)
        tmp_df['dist_to_vil'] =tmp_df.apply(lambda row: haversine(row['lon'],row['lat'],vil_lon,vil_lat), axis=1)
        intensityOverDsqrt = list(tmp_df['intensity']/(tmp_df['dist_to_vil']))
        m1 = max(intensityOverDsqrt)
        tmp_df['datetime'][[i for i, j in enumerate(intensityOverDsqrt) if j == m1]]
        t1 = tmp_df['datetime'][[i for i, j in enumerate(intensityOverDsqrt) if j == m1]].values[0]

        typhoon = typhoon2
        tmp_df = path_df.query("eName=='{}'".format(typhoon))
        tmp_df = pd.DataFrame(list(tmp_df['path'].values)[0])
        tmp_df['lon'] = tmp_df['lon'].astype(float)
        tmp_df['lat'] = tmp_df['lat'].astype(float)
        tmp_df['intensity'] = tmp_df['intensity'].astype(float)
        tmp_df['dist_to_vil'] =tmp_df.apply(lambda row: haversine(row['lon'],row['lat'],vil_lon,vil_lat), axis=1)
        intensityOverDsqrt = list(tmp_df['intensity']/(tmp_df['dist_to_vil']))
        m2 = max(intensityOverDsqrt)
        tmp_df['datetime'][[i for i, j in enumerate(intensityOverDsqrt) if j == m2]]
        t2 = tmp_df['datetime'][[i for i, j in enumerate(intensityOverDsqrt) if j == m2]].values[0]
        
        if m1 >= m2:
            return [m1, t1]
        else:
            return [m2, t2]
    except:
        return [None, None]
def find_strong_strength_(typhoon,vil_lon,vil_lat,path_df):
    try:
        if typhoon == 'MERANTIANDMALAKAS':
            typhoon1= 'MERANTI'
            typhoon2= 'MALAKAS'
            return find_strong_strength_double_(typhoon1,typhoon2,vil_lon,vil_lat,path_df)
        
        else:
            if typhoon == 'NESATANDHAITANG':
                typhoon = 'NESAT' 
            tmp_df = path_df.query("eName=='{}'".format(typhoon))
            tmp_df = pd.DataFrame(list(tmp_df['path'].values)[0])
            tmp_df['lon'] = tmp_df['lon'].astype(float)
            tmp_df['lat'] = tmp_df['lat'].astype(float)
            tmp_df['intensity'] = tmp_df['intensity'].astype(float)
            tmp_df['dist_to_vil'] =tmp_df.apply(lambda row: haversine(row['lon'],row['lat'],vil_lon,vil_lat), axis=1)
            intensityOverDsqrt = list(tmp_df['intensity']/(tmp_df['dist_to_vil']))
            m = max(intensityOverDsqrt)
            tmp_df['datetime'][[i for i, j in enumerate(intensityOverDsqrt) if j == m]]
            return [m, tmp_df['datetime'][[i for i, j in enumerate(intensityOverDsqrt) if j == m]].values[0]]
    except:
        print(typhoon,vil_lon,vil_lat)
        return [None, None]

df['max_intensityOverD'] = df.apply(lambda row: find_strong_strength_(row['typhoon'],row['vil_lon'],row['vil_lat'],path_df), axis=1)

b =[math.log2(i[0]*10000) for i in df['max_intensityOverD']]
df['max_intensityOverD_time_10000_log2'] = b