
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import shapefile #pip install pyshp
from geopy.distance import vincenty
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import KMeans
import glob
import os


# In[2]:


path = 'D:/Users/Qoo/Desktop/taipower/data/'


# In[3]:


# import observation stations' lat-lon data
obs_station = pd.read_csv(path + 'obs_station/obs_intro.csv',encoding='big5',usecols=[0,1,2,3,4,5,6])
old_names = list(obs_station.columns)
new_names = ['stno','stname','st_height','st_lon','st_lat','st_city','st_address']
obs_station.rename(columns=dict(zip(old_names,new_names)),inplace=True)
obs_station.stno = obs_station.stno.str.encode('big5')

# delete unused obs station
obs_station = obs_station[0:33]


# In[4]:


# import observation stations' rainfall data
all_files = glob.glob(os.path.join(path+'typhoon_rain/','*.csv'))
for file in all_files:
    try:
        pd.read_csv(file,encoding='big5',usecols=[0,1,2,3])
    except:
        print 'error at %s' %file

tp_rain = pd.concat(pd.read_csv(file,encoding='big5') for file in all_files )
tp_rain['stno'] = tp_rain['stno'].astype('str')
tp_rain['typhoon'] =  tp_rain['typhoon_name'].str[4:]
tp_rain.accu_end_time = pd.to_datetime(tp_rain.accu_end_time)
tp_rain['day'] = tp_rain.accu_end_time.dt.day

tp_rain.loc[tp_rain.typhoon =='MERANTI','typhoon'] = 'MERANTIANDMALAKAS'
tp_rain.loc[tp_rain.typhoon =='MALAKAS','typhoon'] = 'MERANTIANDMALAKAS'
tp_rain.loc[tp_rain.typhoon =='NESAT','typhoon'] = 'NESATANDHAITANG'
tp_rain.loc[tp_rain.typhoon =='HAITANG','typhoon'] = 'NESATANDHAITANG'

# check unmatch station
tp_rain2 = pd.merge(tp_rain,obs_station,how='left',on='stno')
key = tp_rain2.stname.isnull()
tp_rain2[key].stno.value_counts()


# In[5]:


# import Taiwan village lat-lon dataset
def read_shapefile(shp_path):
	"""
	Read a shapefile into a Pandas dataframe with a 'coords' column holding
	the geometry information. This uses the pyshp package
	"""
	import shapefile

	#read file, parse out the records and shapes
	sf = shapefile.Reader(shp_path)
	fields = [x[0] for x in sf.fields][1:]
	records = sf.records()
	shps = [s.points for s in sf.shapes()]

	#write into a dataframe
	df = pd.DataFrame(columns=fields, data=records)
	df = df.assign(coords=shps)

	return df

vil_latlon = read_shapefile(path + "village_latlon/VILLAGE_MOI_1060831.shp")

# compute village central point
for element in range(0,len(vil_latlon)):
    vil_latlon.loc[element,'vil_lon'] = pd.DataFrame(vil_latlon.coords[element]).mean()[0]
    vil_latlon.loc[element,'vil_lat'] = pd.DataFrame(vil_latlon.coords[element]).mean()[1]
vil_latlon = vil_latlon.iloc[:,[0,1,2,3,11,12]]

# impute missing village & delete unused village
vil_latlon.loc[0,['VILLCODE','VILLNAME']] = ['10013030023','大鵬里']
vil_latlon = vil_latlon.loc[vil_latlon.VILLNAME !='',:]
vil_latlon = vil_latlon.reset_index(drop=True)


# In[6]:


# import df generated from data_manipulation1
df = pd.read_csv(path + 'df.csv')


# In[7]:


# pair each village with its nearest observation station
obs_station.loc[:,'st_lonlat'] = obs_station.loc[:,['st_lon','st_lat']].apply(tuple,axis=1)
vil_latlon.loc[:,'vil_lonlat'] = vil_latlon.loc[:,['vil_lon','vil_lat']].apply(tuple,axis=1)

# find the closet obs station to village
def closest(point, points):
    distance = [vincenty(point, i).miles for i in points]
    return distance.index(min(distance))

for i in range(0,len(vil_latlon)):
    vil_latlon.loc[i,'stno_index'] = closest(vil_latlon.loc[i,'vil_lonlat'], obs_station.loc[:,'st_lonlat'])
obs_station.loc[:,'stno_index'] = obs_station.index
vil_latlon2 = pd.merge(vil_latlon, obs_station, how='left', on='stno_index')
vil_latlon2 = vil_latlon2.iloc[:,[0,1,2,3,4,5,8,9,10,11,12,13]]
vil_latlon2.to_csv(path +'village_intro.csv',encoding='utf-8')

# check unmatch village and obs station
key = vil_latlon2.stno.isnull()
vil_latlon2[key]


# In[9]:


# deal with ViLCode
for i in range(0,len(vil_latlon2)):
    if vil_latlon2.loc[i,'VILLCODE'][3:5] =='00':
        vil_latlon2.loc[i,'VilCode'] = vil_latlon2.loc[i,'VILLCODE'][0:3] +  vil_latlon2.loc[i,'VILLCODE'][5:7] + '00-'+  vil_latlon2.loc[i,'VILLCODE'][8:11]
    else:
        vil_latlon2.loc[i,'VilCode'] = vil_latlon2.loc[i,'VILLCODE'][0:7] +  '-'+  vil_latlon2.loc[i,'VILLCODE'][8:11]


# In[10]:


df2 = pd.merge(df,vil_latlon2,how='left', on='VilCode')


# In[11]:


# find unmatch region
key = df2.stno.isnull()
miss = df2[key]
miss.groupby(['CityName','TownName','VilName']).size().reset_index()


# In[ ]:


'''
# df 多出 大鵬里
print set(df.VilCode) - set(vil_latlon2.VilCode)
#df.loc[df.VilCode=='1001303-023',:]

# vil_latlon 多出 中崙里
print set(vil_latlon2.VilCode) - set(df.VilCode)
vil_latlon2.loc[vil_latlon2.VilCode =='1000401-031',:]
'''


# In[12]:


# check whether all obs station have rainfall records
print len(np.unique(tp_rain.stno))
print len(np.unique(df2.stno))
print set(df2.stno) - set(tp_rain.stno)
print set(tp_rain.stno) - set(df2.stno)
obs_station.loc[(obs_station.stno =='467790')|(obs_station.stno =='466850'),:]


# In[13]:


# mean hourly rainfall
mean_hour_rain = tp_rain.groupby(['typhoon','stno'], as_index=False).agg({'accu_value':'mean'})
mean_hour_rain.columns.values[2] = 'mean_accu_hour_rain'

# mean daily rainfall
mean_day_rain = tp_rain.groupby(['day','typhoon','stno'], as_index=False).agg({'accu_value':'sum'})
mean_day_rain = mean_day_rain.groupby(['typhoon','stno'], as_index=False).agg({'accu_value':'mean'})
mean_day_rain.columns.values[2] = 'mean_accu_day_rain'

# accu rainfall
total_rain = tp_rain.groupby(['typhoon','stno'], as_index=False).agg({'accu_value':'sum'})
total_rain.columns.values[2] = 'accu_rain'

#達到幾次大雨指標(每日累積降雨 80MM以上)
# number of times daily accu rainfall > 80 mm
heavy_rain = tp_rain.groupby(['day','typhoon','stno'], as_index=False).agg({'accu_value':'sum'})
heavy_rain_times = heavy_rain.loc[heavy_rain.accu_value >= 80,:].groupby(['typhoon','stno'], 
                as_index=False).agg({'accu_value':'count'})
heavy_rain_times.columns.values[2] = 'heavy_rain_count_rule1'

#達到幾次大雨指標(每小時累積降雨 40MM以上)
# number of times hourly accu rainfall > 40 mm
heavy_rain_times2 = tp_rain.loc[tp_rain.accu_value >=40,:].groupby(['typhoon','stno'],as_index=False).agg({'accu_value':'count'})
heavy_rain_times2.columns.values[2] = 'heavy_rain_count_rule2'

#達到幾次豪雨指標(每日累積降雨 200MM以上)
# number of times daily accu rainfall > 200 mm
how_rain = tp_rain.groupby(['day','typhoon','stno'], as_index=False).agg({'accu_value':'sum'})
how_rain_times1 = how_rain.loc[how_rain.accu_value >= 200,:].groupby(['typhoon','stno'], 
                as_index=False).agg({'accu_value':'count'})
how_rain_times1.columns.values[2] = 'how_rain_count_rule1'

#達到幾次大豪雨指標(每日累積降雨 350MM以上)
# number of times daily accu rainfall > 350 mm
big_how_rain = tp_rain.groupby(['day','typhoon','stno'], as_index=False).agg({'accu_value':'sum'})
big_how_rain_times = big_how_rain.loc[big_how_rain.accu_value >= 350,:].groupby(['typhoon','stno'], 
                as_index=False).agg({'accu_value':'count'})
big_how_rain_times.columns.values[2] = 'big_how_rain_count'

#達到幾次超大豪雨指標(每日累積降雨 500MM以上)
# number of times daily accu rainfall > 500 mm
big_big_how_rain = tp_rain.groupby(['day','typhoon','stno'], as_index=False).agg({'accu_value':'sum'})
big_big_how_rain_times = big_big_how_rain.loc[big_big_how_rain.accu_value >= 500,:].groupby(['typhoon','stno'], 
                as_index=False).agg({'accu_value':'count'})
big_big_how_rain_times.columns.values[2] = 'big_big_how_rain_count'

#不同颱風在各測站下的每小時最大累積雨量
# max hourly rainfall
max_hour_rain = tp_rain.groupby(['typhoon','stno'], as_index=False).agg({'accu_value':'max'})
max_hour_rain.columns.values[2] = 'max_hour_accu_rain'
#不同颱風在各測站下的每日最大累積雨量
# max daily accu rainfall
max_day_rain = tp_rain.groupby(['day','typhoon','stno'], as_index=False).agg({'accu_value':'sum'}).groupby(['typhoon','stno'], as_index=False).agg({'accu_value':'max'})
max_day_rain.columns.values[2] = 'max_day_accu_rain'


# In[14]:


df2 = pd.merge(df2, mean_hour_rain, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, mean_day_rain, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, total_rain, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, heavy_rain_times, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, heavy_rain_times2, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, how_rain_times1, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, big_how_rain_times, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, big_big_how_rain_times, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, max_hour_rain, on=['stno','typhoon'],how ='left')
df2 = pd.merge(df2, max_day_rain, on=['stno','typhoon'],how ='left')


# In[15]:


# impute missing value
# note: 1. as to two obs station don't have rainfall records. 2. various rainfall index
df3 = pd.concat([ df2.iloc[:,0:55], df2.iloc[:,55:65].fillna(0)],axis=1)


# In[16]:


#import obs stations' typhoon wind data 
all_files = glob.glob(os.path.join(path+'typhoon_wind/','*.csv'))
for file in all_files:
    try:
        pd.read_csv(file,encoding='big5',usecols=[0,1,2,3])
    except:
        print 'error at %s' %file

tp_wind = pd.concat(pd.read_csv(file,encoding='big5') for file in all_files )


# In[17]:


# seperately process on typhoon max wind speed  & wind gust
tp_wm = tp_wind.iloc[:,[0,2,4,5,6,7,8]]
tp_wg = tp_wind.iloc[:,[0,1,3,5,6,7,8]]

# drop unreasonable data
tp_wm = tp_wm.loc[tp_wm.WSMax >0,]
tp_wg = tp_wg.loc[tp_wg.WSGust >0,]

# preprocess
tp_wm['stno'] = tp_wm['stno'].astype('str')
tp_wm['typhoon'] = tp_wm.typhoon_name.str[4:]
tp_wm.ObsTime = pd.to_datetime(tp_wm.ObsTime)
tp_wm['day'] = tp_wm.ObsTime.dt.day
tp_wm.loc[tp_wm.typhoon =='MERANTI','typhoon'] = 'MERANTIANDMALAKAS'
tp_wm.loc[tp_wm.typhoon =='MALAKAS','typhoon'] = 'MERANTIANDMALAKAS'
tp_wm.loc[tp_wm.typhoon =='NESAT','typhoon'] = 'NESATANDHAITANG'
tp_wm.loc[tp_wm.typhoon =='HAITANG','typhoon'] = 'NESATANDHAITANG'

tp_wg['stno'] = tp_wg['stno'].astype('str')
tp_wg['typhoon'] = tp_wg.typhoon_name.str[4:]
tp_wg.ObsTime = pd.to_datetime(tp_wg.ObsTime)
tp_wg['day'] = tp_wg.ObsTime.dt.day
tp_wg.loc[tp_wg.typhoon =='MERANTI','typhoon'] = 'MERANTIANDMALAKAS'
tp_wg.loc[tp_wg.typhoon =='MALAKAS','typhoon'] = 'MERANTIANDMALAKAS'
tp_wg.loc[tp_wg.typhoon =='NESAT','typhoon'] = 'NESATANDHAITANG'
tp_wg.loc[tp_wg.typhoon =='HAITANG','typhoon'] = 'NESATANDHAITANG'

tp_wm.loc[tp_wm.WDMax ==550,'WDMax'] = 190
tp_wm.loc[tp_wm.WDMax ==999.9,'WDMax'] = 279.9


# In[18]:


# mean hourly max wind speed
#平均每小時最大風速
mean_hr_wsm = tp_wm.groupby(['typhoon','stno'], as_index=False).agg({'WSMax':'mean'})
mean_hr_wsm.columns.values[2] = 'mean_hr_wsmax'

# mean hourly wind gust
#平均每小時瞬間極大風速
mean_hr_wsg = tp_wg.groupby(['typhoon','stno'], as_index=False).agg({'WSGust':'mean'})
mean_hr_wsg.columns.values[2] = 'mean_hr_wsgust'

# max hourly max wind speed
#最大小時風速
max_hr_wsm = tp_wm.groupby(['typhoon','stno'], as_index=False).agg({'WSMax':'max'})
max_hr_wsm.columns.values[2] = 'max_hr_wsmax'

# max hourly wind gust
#最大小時瞬間極大風速
max_hr_wsg = tp_wg.groupby(['typhoon','stno'], as_index=False).agg({'WSGust':'max'})
max_hr_wsg.columns.values[2] = 'max_hr_wsgust'

# the number of times max wind speed > 20.8 
#測站測得颱風最大風速每小時達到烈風以上的總次數
total_daily_sum_WSM = tp_wm.loc[tp_wm.WSMax >20.8,:].groupby(['typhoon','stno'], as_index=False).agg({'WSMax':'count'})
total_daily_sum_WSM.columns.values[2] = 'total_daily_sum_WSMax'

# the number of times wind gust > 20.8
#測站測得颱風瞬間極大風速每小時達到烈風以上的總次數
total_daily_sum_WSG =tp_wg.loc[tp_wg.WSGust >20.8,:].groupby(['typhoon','stno'], as_index=False).agg({'WSGust':'count'})
total_daily_sum_WSG.columns.values[2] = 'total_daily_sum_WSGust'


# In[19]:


df3 = pd.merge(df3, mean_hr_wsm, on=['stno','typhoon'],how ='left')
df3 = pd.merge(df3, mean_hr_wsg, on=['stno','typhoon'],how ='left')
df3 = pd.merge(df3, max_hr_wsm, on=['stno','typhoon'],how ='left')
df3 = pd.merge(df3, max_hr_wsg, on=['stno','typhoon'],how ='left')
df3 = pd.merge(df3, total_daily_sum_WSM, on=['stno','typhoon'],how ='left')
df3 = pd.merge(df3, total_daily_sum_WSG, on=['stno','typhoon'],how ='left')


# In[20]:


# impute missing value
df3[['mean_hr_wsmax',
       'mean_hr_wsgust', 'max_hr_wsmax', 'max_hr_wsgust',
       'total_daily_sum_WSMax', 'total_daily_sum_WSGust']] = df3[['mean_hr_wsmax',
       'mean_hr_wsgust', 'max_hr_wsmax', 'max_hr_wsgust',
       'total_daily_sum_WSMax', 'total_daily_sum_WSGust']].fillna(0)


# In[21]:


# wind direction
tp_wm.loc[(tp_wm.WDMax == 0) | (tp_wm.WDMax == 360),'wind_direction_max'] = 1
tp_wm.loc[(tp_wm.WDMax > 0) & (tp_wm.WDMax < 90),'wind_direction_max'] = 2
tp_wm.loc[tp_wm.WDMax == 90,'wind_direction_max'] = 3
tp_wm.loc[(tp_wm.WDMax > 90) & (tp_wm.WDMax < 180),'wind_direction_max'] = 4
tp_wm.loc[tp_wm.WDMax == 180,'wind_direction_max'] = 5
tp_wm.loc[(tp_wm.WDMax > 180) & (tp_wm.WDMax < 270),'wind_direction_max'] = 6
tp_wm.loc[tp_wm.WDMax == 270,'wind_direction_max'] = 7
tp_wm.loc[(tp_wm.WDMax > 270) & (tp_wm.WDMax < 360),'wind_direction_max'] = 8
tp_wm.loc[tp_wm.WDMax == 550,'wind_direction_max'] = 6
tp_wm.loc[tp_wm.WDMax == 999.9,'wind_direction_max'] = 8

tp_wg.loc[(tp_wg.WDGust == 0) | (tp_wg.WDGust == 360),'wind_direction_gust'] = 1
tp_wg.loc[(tp_wg.WDGust > 0) & (tp_wg.WDGust < 90),'wind_direction_gust'] = 2
tp_wg.loc[tp_wg.WDGust == 90,'wind_direction_gust'] = 3
tp_wg.loc[(tp_wg.WDGust > 90) & (tp_wg.WDGust < 180),'wind_direction_gust'] = 4
tp_wg.loc[tp_wg.WDGust == 180,'wind_direction_gust'] = 5
tp_wg.loc[(tp_wg.WDGust > 180) & (tp_wg.WDGust < 270),'wind_direction_gust'] = 6
tp_wg.loc[tp_wg.WDGust == 270,'wind_direction_gust'] = 7
tp_wg.loc[(tp_wg.WDGust > 270) & (tp_wg.WDGust < 360),'wind_direction_gust'] = 8


# In[22]:


# wind speed of each direction
tp_wm = tp_wm.pivot_table(index=['ObsTime','typhoon','stno'],columns='wind_direction_max',values='WSMax').reset_index()
tp_wg = tp_wg.pivot_table(index=['ObsTime','typhoon','stno'],columns='wind_direction_gust',values='WSGust').reset_index()


# In[23]:


# impute missing value
tp_wm = tp_wm.fillna(0)
tp_wg = tp_wg.fillna(0)


# In[24]:


# mean/max wind speed of each direction
mean_tp_wm = tp_wm.groupby(['typhoon','stno'],as_index=False).agg({1.0:'mean',2.0:'mean',3.0:'mean',
                                      5.0:'mean',6.0:'mean',8.0:'mean'})
mean_tp_wg = tp_wg.groupby(['typhoon','stno'],as_index=False).agg({1.0:'mean',2.0:'mean',3.0:'mean',
                                      5.0:'mean',6.0:'mean',8.0:'mean'})
max_tp_wm = tp_wm.groupby(['typhoon','stno'],as_index=False).agg({1.0:'max',2.0:'max',3.0:'max',
                                      5.0:'max',6.0:'max',8.0:'max'})
max_tp_wg = tp_wg.groupby(['typhoon','stno'],as_index=False).agg({1.0:'max',2.0:'max',3.0:'max',
                                      5.0:'max',6.0:'max',8.0:'max'})


# In[25]:


# rename colmn
mean_tp_wm.columns.values[2:8] = ['mean_1D_wm','mean_2D_wm','mean_3D_wm','mean_5D_wm','mean_6D_wm','mean_8D_wm']
mean_tp_wg.columns.values[2:8] = ['mean_1D_wg','mean_2D_wg','mean_3D_wg','mean_5D_wg','mean_6D_wg','mean_8D_wg']
max_tp_wm.columns.values[2:8] = ['max_1D_wm','max_2D_wm','max_3D_wm','max_5D_wm','max_6D_wm','max_8D_wm']
max_tp_wg.columns.values[2:8] = ['max_1D_wg','max_2D_wg','max_3D_wg','max_5D_wg','max_6D_wg','max_8D_wg']


# In[26]:


df4 = pd.merge(df3, mean_tp_wm, on=['stno','typhoon'],how ='left')
df4 = pd.merge(df4, mean_tp_wg, on=['stno','typhoon'],how ='left')
df4 = pd.merge(df4, max_tp_wm, on=['stno','typhoon'],how ='left')
df4 = pd.merge(df4, max_tp_wg, on=['stno','typhoon'],how ='left')


# In[27]:


# impute missing value
df4[['mean_1D_wm',
       'mean_2D_wm', 'mean_3D_wm', 'mean_5D_wm', 'mean_6D_wm',
       'mean_8D_wm', 'mean_1D_wg', 'mean_2D_wg', 'mean_3D_wg',
       'mean_5D_wg', 'mean_6D_wg', 'mean_8D_wg', 'max_1D_wm', 'max_2D_wm',
       'max_3D_wm', 'max_5D_wm', 'max_6D_wm', 'max_8D_wm', 'max_1D_wg',
       'max_2D_wg', 'max_3D_wg', 'max_5D_wg', 'max_6D_wg', 'max_8D_wg']] = df4[['mean_1D_wm',
       'mean_2D_wm', 'mean_3D_wm', 'mean_5D_wm', 'mean_6D_wm',
       'mean_8D_wm', 'mean_1D_wg', 'mean_2D_wg', 'mean_3D_wg',
       'mean_5D_wg', 'mean_6D_wg', 'mean_8D_wg', 'max_1D_wm', 'max_2D_wm',
       'max_3D_wm', 'max_5D_wm', 'max_6D_wm', 'max_8D_wm', 'max_1D_wg',
       'max_2D_wg', 'max_3D_wg', 'max_5D_wg', 'max_6D_wg', 'max_8D_wg']].fillna(0)


# In[ ]:


'''
# mean wind direction
mean_wdm = tp_wm.groupby(['typhoon','stno'], as_index=False).agg({'WDMax':'mean'})
mean_wdm.columns.values[2] = 'mean_wdmax'
mean_wdg = tp_wg.groupby(['typhoon','stno'], as_index=False).agg({'WDGust':'mean'})
mean_wdg.columns.values[2] = 'mean_wdgust'

df4 = pd.merge(df4, mean_wdm, on=['stno','typhoon'],how ='left')
df4 = pd.merge(df4, mean_wdg, on=['stno','typhoon'],how ='left')
df4[['mean_wdmax','mean_wdgust']] = df4[['mean_wdmax','mean_wdgust']].fillna(0)
'''


# In[ ]:


'''
#交互作用
tp_wind['WSD_M'] = tp_wind.WSMax *tp_wind.wind_direction_max
tp_wind['WSD_G'] = tp_wind.WSGust * tp_wind.wind_direction_gust
sd1 = tp_wind.groupby(['typhoon','stno'], as_index=False).agg({'WSD_M':'mean'})
sd1.columns.values[2] = 'mean_WSDmax'
sd2 = tp_wind.groupby(['typhoon','stno'], as_index=False).agg({'WSD_M':'max'})
sd2.columns.values[2] = 'max_WSDmax'
sd3 = tp_wind.groupby(['typhoon','stno'], as_index=False).agg({'WSD_G':'mean'})
sd3.columns.values[2] = 'mean_WSDgust'
sd4 = tp_wind.groupby(['typhoon','stno'], as_index=False).agg({'WSD_G':'mean'})
sd4.columns.values[2] = 'max_WSDgust'
df4 = pd.merge(df4, sd1, on=['stno','typhoon'],how ='left')
df4 = pd.merge(df4, sd2, on=['stno','typhoon'],how ='left')
df4 = pd.merge(df4, sd3, on=['stno','typhoon'],how ='left')
df4 = pd.merge(df4, sd4, on=['stno','typhoon'],how ='left')
'''


# In[34]:


# potential landslide river to city
City_danger_river_num = pd.read_csv(path +'City_danger_river_num.csv')
df4 = pd.merge(df4, City_danger_river_num, how='left', on='CityName')

# impute missing value
df5 = df4.fillna(0)


# In[36]:


# region clustering by lat-lon
kmeans = KMeans(n_clusters=20, random_state=2017).fit(df5[['vil_lon','vil_lat']])
df5['region_cluster'] = kmeans.predict(df5[['vil_lon','vil_lat']])


# In[37]:


# number of landslide alert by typhoon
landslide = pd.read_csv(path+'landslide_alert.csv' )
df6 = pd.merge(df5, landslide, how='left', on=['typhoon','year'])


# In[ ]:


df6.to_csv(path +'df.csv',encoding='utf-8',index=False)

