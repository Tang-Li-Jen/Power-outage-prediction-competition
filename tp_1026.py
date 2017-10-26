
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os
import glob
from sklearn.ensemble import RandomForestRegressor


# In[2]:


# 匯入訓練與測試資料 import dataset
data_path = 'D:\\Users\\Qoo\\Desktop\\taipower\\data\\'
train = pd.read_csv(data_path + 'train.csv')
test = pd.read_csv(data_path+ 'submit.csv')

# merge train and test data
df = pd.merge(train,test,how='inner',
        on=['CityName','TownName','VilName','VilCode'])

#transpose columns to rows
var_names = list(df.columns)
df2 = pd.melt(df,id_vars=['CityName','TownName','VilName','VilCode'],value_vars=var_names[4:len(var_names)],
              var_name='typhoon',value_name='elect_down')


# In[3]:


# 颱風警報資料庫 http://rdc28.cwb.gov.tw/TDB/ntdb/pageControl/ty_warning
typhoon = pd.read_csv(data_path + 'typhoon_alert.csv',encoding='big5')
#取出颱風警報時間 方法來源 https://opensourcehacker.com/2011/02/23/tuplifying-a-list-or-pairs-in-python/
i = iter(list(typhoon.duration))
duration = zip(i,i)
typhoon_time = pd.DataFrame(duration, columns=['arrive','leave'])

#合併颱風資料與警報時間
cols = list(typhoon)
cols.remove('duration')
tp = typhoon.loc[0:len(typhoon):2,cols]
tp = tp.reset_index(drop=True)
tp2 = pd.concat([tp,typhoon_time],axis=1,join_axes=[tp.index])

#取出訓練與預測資料的時間區間
tp2.arrive = pd.to_datetime(tp2.arrive)
tp2.leave = pd.to_datetime(tp2.leave)
tp2.year = tp2.arrive.dt.year
mask = (tp2.year >=2014) & (tp2.year<=2017)
tp3 = tp2[mask]
#取出的颱風總數
print 'total number of typhoon : %s' %len(tp3)

#找出颱風資料庫尚未有的颱風資料
set(df2.typhoon.str.upper()) - set(tp3.en_name)


# In[4]:


# MERANTIANDMALAKAS
MERANTIANDMALAKAS = tp3.loc[(tp3.en_name =='MALAKAS') | (tp3.en_name =='MERANTI'),]
#print MERANTIANDMALAKAS
tp3.loc[19,6:11] = MERANTIANDMALAKAS.iloc[:,6:11].astype(np.int16).mean()
tp3.iloc[19,[0,1,2,3,4,5,11,12]] = [2016,201615,u'莫蘭蒂及馬勒卡',u'MERANTIANDMALAKAS','7',u'強烈',pd.to_datetime('2016-09-12 23:30:00'),pd.to_datetime('2016-09-18 08:30')]


# In[5]:


# NESATANDHAITANG
NESATANDHAITANG = tp3.loc[(tp3.en_name =='NESAT') | (tp3.en_name =='HAITANG'),]
#print NESATANDHAITANG
tp3.loc[20,6:11] = NESATANDHAITANG.iloc[:,[6,7,8,10]].astype(np.int16).mean()
tp3.iloc[20,[0,1,2,3,4,5,9,11,12]] = [2017,201711,u'尼莎及海棠',u'NESATANDHAITANG','---',u'中度',60,pd.to_datetime('2017-07-28 08:30'),pd.to_datetime('2017-07-31 08:30')]


# In[6]:


df2.typhoon = df2.typhoon.str.upper()
df3 = pd.merge(df2, tp3, how='left',left_on='typhoon', right_on='en_name' )
print len(df3)

#檢查是否已經蒐集到全部的颱風資料
set(df2.typhoon.str.upper()) - set(tp3.en_name)


# In[16]:


df3.info()


# In[18]:


# r10_km
df3.loc[df3.r10_km =='---','r10_km'] = '0'

#typhoon type
df3.loc[df3.type ==u'---','type'] = 0
df3.loc[df3.type ==u'特殊','type'] = 10

#typhoon magnitude
print df3.magnitude.value_counts()
df3.loc[df3.magnitude ==u'輕度','magnitude'] = 1
df3.loc[df3.magnitude ==u'中度','magnitude'] = 2
df3.loc[df3.magnitude ==u'強烈','magnitude'] = 3

# time-related variables
# arrive 
df3.loc[:,'arrive_month'] = df3.arrive.dt.month
df3.loc[:,'arrive_hour'] = df3.arrive.dt.hour
df3.loc[:,'arrive_weekday'] = df3.arrive.dt.weekday
df3.loc[:,'arrive_week'] = df3.arrive.dt.week
df3.loc[:,'duration'] = df3.leave - df3.arrive
df3.loc[:,'duration_h'] = df3.duration.dt.total_seconds() / 3600

#處理變數型態
df3.year = df3.year.astype('float')
df3.hpa = df3.hpa.astype('float')
df3.wind_speed = df3.wind_speed.astype('float')
df3.r7_km = df3.r7_km.astype('float')
df3.r10_km = df3.r10_km.astype('float')
df3.alert_level = df3.alert_level.astype('float')


# In[ ]:


#pole = pd.read_csv(data_path + u'poledata/北北區處pole.csv',encoding='utf-8',usecols=[0,1,2,3,4,5])
#pole.head()


# In[19]:


#checking file's encode
all_files = glob.glob(os.path.join(data_path+'poledata/','*.csv'))
for file in all_files:
    try:
        pd.read_csv(file,encoding='utf-8',usecols=[0,1,2,3])
    except:
        print 'error at %s' %file


# In[20]:


# import multiple electric pole dataset
print 'total files number : %s' %len(glob.glob(os.path.join(data_path+'poledata/','*.csv')))
pole = pd.concat(pd.read_csv(file,encoding='utf-8',usecols=[0,1,2,3,4]) for file in all_files )


# In[21]:


#檢查總資料筆數是否有誤
L =[]
for file in all_files:
    L.append(len(pd.read_csv(file,encoding='utf-8',usecols=[0])))
if len(pole) == sum(L):
    print 'you are god-damn right!'


# In[22]:


#rename dataframe
old_names = list(pole.columns)
new_names = ['CityName','TownName','VilName','coordinate','p_type']
pole.rename(columns=dict(zip(old_names,new_names)),inplace=True)
pole.head(1)


# In[24]:


#pole.groupby(['CityName','TownName','VilName'],as_index=False).count()
#每個村里有幾類桿子
p1 = pole.groupby(['CityName','TownName','VilName'],as_index=False).agg({'p_type':'nunique'})
p1.columns.values[3] = 'pole_type_counts'
p1.CityName = p1.CityName.replace({u'臺':u'台'},regex=True)
#每個村里下,各類桿子有幾支
p2 = pole.groupby(['CityName','TownName','VilName','p_type'],as_index=False).count()
p2 = p2.pivot_table(index=['CityName','TownName','VilName'],columns='p_type',values='coordinate')
p2 = p2.reset_index()
p2 = p2.fillna(0)
p2.columns.values[3:13] =['p%s' % s for s in range(1,11)] 
p2.CityName = p2.CityName.replace({u'臺':u'台'},regex=True)
# or ['p{}'.format(i) for i in range(1,11)]
#每個村里總共幾支
p3 = pole.groupby(['CityName','TownName','VilName'],as_index=False).count()
p3.columns.values[3] = 'pole_counts'
p3 = p3.iloc[:,[0,1,2,3]]
p3.CityName = p3.CityName.replace({u'臺':u'台'},regex=True)

#transform columns value from unicode to str
for data in [p1,p2,p3]:
    for column in ['CityName','TownName','VilName']:
        data[column] =  data[column].str.encode('utf-8')
#double check encoding
print type(df3.CityName[1])
print type(p1.CityName[1])


# In[26]:


df3.CityName = df3.CityName.replace({'臺':'台'},regex=True)
df3 = pd.merge(df3,p1,how='left',on=['CityName','TownName','VilName'])
df3 = pd.merge(df3,p2,how='left',on=['CityName','TownName','VilName'])
df3 = pd.merge(df3,p3,how='left',on=['CityName','TownName','VilName'])


# In[ ]:


#電桿資料並未包含全部村里 (需要補值)
df3 = df3.fillna(0)


# In[ ]:


#是否為雙颱
df3['double_kill'] = 0
df3.loc[(df3.typhoon =='NESATANDHAITANG')|(df3.typhoon =='MERANTIANDMALAKAS'),'double_kill'] = 1


# In[ ]:


#各鄉鎮市區人口密度 https://data.gov.tw/dataset/8410
pop_files = glob.glob(os.path.join(data_path+'population/','*.csv'))
population = pd.concat(pd.read_csv(d, skiprows=2, nrows=370, names=['Minguo_year','location',
            'people_total','area','population_density'] ) for d in pop_files)
population['CityName'] = population.location.str.slice(0,9)
population['TownName'] = population.location.str.slice(9,)

#處理行政區升格問題
population.CityName = population.CityName.replace({'臺':'台'},regex=True)
population.TownName = population.TownName.replace({'員林鎮':'員林市'},regex=True)
population.TownName = population.TownName.replace({'頭份鎮':'頭份市'},regex=True)

#西元轉民國,以方便合併資料
df3.loc[df3.year == 2017,'Minguo_year'] =105
df3.loc[df3.year == 2016,'Minguo_year'] =105
df3.loc[df3.year == 2015,'Minguo_year'] =104
df3.loc[df3.year == 2014,'Minguo_year'] =103
df3.loc[df3.year == 2013,'Minguo_year'] =102
df3 = pd.merge(df3, population, how='left',on=['CityName','TownName','Minguo_year'] )

City_dummy = pd.get_dummies(df3['CityName'])
City_dummy.columns.values[0:22] =['c%s' % s for s in range(1,23)] 
df3 = pd.concat([df3,City_dummy],axis=1)


# In[ ]:


#檢查內涵字元
#population.loc[population.TownName.str.contains('頭份'),:]

#找出未對應到的資料
#key = df3['people_total'].isnull()
#df3_NA = df3.loc[key]
#df3_NA.groupby(['CityName','TownName','VilName'],as_index=False).agg('count')


# In[ ]:


#list(set(df3.typhoon))


# In[ ]:


#split data to train and test
te = df3.loc[(df3.typhoon=='NESATANDHAITANG')|(df3.typhoon=='MEGI'),:]
keep = list(set(df3.index) - set(te.index))
tr = df3.iloc[keep,:]
print len(te)
print len(tr)
print len(df3)


# In[ ]:


#tr.typhoon.value_counts()


# In[ ]:


#te.typhoon.value_counts()


# In[ ]:


var = ['year','type','magnitude','hpa','wind_speed','r7_km','r10_km','alert_level','arrive_month','arrive_hour',
       'arrive_weekday','arrive_week','duration_h','pole_type_counts',
 'p1', 'p2', 'p3','p4','p5','p6','p7','p8','p9', 'p10',
       'pole_counts','double_kill', 'people_total','area','population_density',
            'c1',
 'c2',
 'c3',
 'c4',
 'c5',
 'c6',
 'c7',
 'c8',
 'c9',
 'c10',
 'c11',
 'c12',
 'c13',
 'c14',
 'c15',
 'c16',
 'c17',
 'c18',
 'c19',
 'c20',
 'c21',
 'c22']
#'CityName','TownName','VilName','VilCode'
tr_x = tr.loc[:,var]
tr_y = tr.loc[:,'elect_down']
te_N = te.loc[te.typhoon =='NESATANDHAITANG', var]
te_M = te.loc[te.typhoon =='MEGI', var]
print len(tr_x) , len(tr_y)
print len(te_N) , len(te_M)


# In[ ]:



regr = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=2017, oob_score=True)
regr.fit(tr_x, tr_y)


# In[ ]:


regr.oob_score_


# In[ ]:


Nes = regr.predict(te_N)
Meg = regr.predict(te_M)
print len(Nes)
print len(Meg)


# In[ ]:


test.NesatAndHaitang = Nes
test.Megi = Meg


# In[ ]:


test.describe()


# In[ ]:


print len(test)
set(train.VilCode) - set(test.VilCode)


# In[ ]:


test.to_csv(data_path+ 'sub.csv',index=False)

