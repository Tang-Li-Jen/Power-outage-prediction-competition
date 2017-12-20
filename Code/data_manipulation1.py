
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os
import glob


# In[2]:


# import training and testing dataset
data_path = 'D:\\Users\\Qoo\\Desktop\\taipower\\data\\'
train = pd.read_csv(data_path + 'train.csv')
test = pd.read_csv(data_path+ 'submit.csv')

# merge training and testing data
df = pd.merge(train,test,how='inner',
        on=['CityName','TownName','VilName','VilCode'])

# transpose columns to rows
var_names = list(df.columns)
df2 = pd.melt(df,id_vars=['CityName','TownName','VilName','VilCode'],value_vars=var_names[4:len(var_names)],
              var_name='typhoon',value_name='elect_down')


# In[3]:


# typhoon alert dataset 
# data source: http://rdc28.cwb.gov.tw/TDB/ntdb/pageControl/ty_warning
typhoon = pd.read_csv(data_path + 'typhoon_alert.csv',encoding='big5')

# extract typhoon alert period 
i = iter(list(typhoon.duration))
duration = zip(i,i)
typhoon_time = pd.DataFrame(duration, columns=['arrive','leave'])
cols = list(typhoon)
cols.remove('duration')
tp = typhoon.loc[0:len(typhoon):2,cols]
tp = tp.reset_index(drop=True)
tp2 = pd.concat([tp,typhoon_time],axis=1,join_axes=[tp.index])
tp2.arrive = pd.to_datetime(tp2.arrive)
tp2.leave = pd.to_datetime(tp2.leave)
tp2.year = tp2.arrive.dt.year

# extract typhoon alert between training set time period
mask = (tp2.year >=2014) & (tp2.year<=2017)
tp3 = tp2[mask]

print 'total number of typhoon alert : %s' %len(tp3)
# ckeck missing typhoon alert data in df2 
print set(df2.typhoon.str.upper()) - set(tp3.en_name)


# In[4]:


# create values for two special typhoons
# MERANTIANDMALAKAS
MERANTIANDMALAKAS = tp3.loc[(tp3.en_name =='MALAKAS') | (tp3.en_name =='MERANTI'),]
#print MERANTIANDMALAKAS
tp3.loc[19,6:11] = MERANTIANDMALAKAS.iloc[:,6:11].astype(np.int16).max()
tp3.iloc[19,[0,1,2,3,4,5,11,12]] = [2016,201615,u'莫蘭蒂及馬勒卡',u'MERANTIANDMALAKAS','7',u'強烈',pd.to_datetime('2016-09-12 23:30:00'),pd.to_datetime('2016-09-18 08:30')]

# NESATANDHAITANG
NESATANDHAITANG = tp3.loc[(tp3.en_name =='NESAT') | (tp3.en_name =='HAITANG'),]
#print NESATANDHAITANG
tp3.loc[20,6:11] = NESATANDHAITANG.iloc[:,[6,7,8,10]].astype(np.int16).max()
tp3.iloc[20,[0,1,2,3,4,5,9,11,12]] = [2017,201711,u'尼莎及海棠',u'NESATANDHAITANG','---',u'中度',60,pd.to_datetime('2017-07-28 08:30'),pd.to_datetime('2017-07-31 08:30')]


# In[5]:


df2.typhoon = df2.typhoon.str.upper()
df3 = pd.merge(df2, tp3, how='left',left_on='typhoon', right_on='en_name' )
print len(df3)

#ckeck we have all typhoon alert data
set(df2.typhoon.str.upper()) - set(tp3.en_name)


# In[6]:


# process on typhoon alert variables
# r10_km
df3.loc[df3.r10_km =='---','r10_km'] = '0'

#typhoon type
df3.loc[df3.type ==u'---','type'] = 0
df3.loc[df3.type ==u'特殊','type'] = 10

#typhoon magnitude
df3.loc[df3.magnitude ==u'輕度','magnitude'] = 1
df3.loc[df3.magnitude ==u'中度','magnitude'] = 2
df3.loc[df3.magnitude ==u'強烈','magnitude'] = 3

# time-related variables on arrive_datetime 
df3.loc[:,'arrive_month'] = df3.arrive.dt.month
df3.loc[:,'arrive_hour'] = df3.arrive.dt.hour
df3.loc[:,'arrive_weekday'] = df3.arrive.dt.weekday
df3.loc[:,'arrive_week'] = df3.arrive.dt.week
df3.loc[:,'duration'] = df3.leave - df3.arrive
df3.loc[:,'duration_h'] = df3.duration.dt.total_seconds() / 3600

df3.year = df3.year.astype('float')
df3.hpa = df3.hpa.astype('float')
df3.wind_speed = df3.wind_speed.astype('float')
df3.r7_km = df3.r7_km.astype('float')
df3.r10_km = df3.r10_km.astype('float')
df3.alert_level = df3.alert_level.astype('float')


# In[7]:


#check electric pole files' encoding
all_files = glob.glob(os.path.join(data_path+'poledata/','*.csv'))
for file in all_files:
    try:
        pd.read_csv(file,encoding='utf-8',usecols=[0,1,2,3])
    except:
        print 'error at %s' %file


# In[8]:


# import multiple electric pole dataset
print 'total files number : %s' %len(glob.glob(os.path.join(data_path+'poledata/','*.csv')))
pole = pd.concat(pd.read_csv(file,encoding='utf-8',usecols=[0,1,2,3,4]) for file in all_files )


# In[9]:


#rename dataframe
old_names = list(pole.columns)
new_names = ['CityName','TownName','VilName','coordinate','p_type']
pole.rename(columns=dict(zip(old_names,new_names)),inplace=True)


# In[10]:


#check total sample size is correct
L =[]
for file in all_files:
    L.append(len(pd.read_csv(file,encoding='utf-8',usecols=[0])))
if len(pole) == sum(L):
    print 'you are god-damn right!'


# In[11]:


print 'number of unique VilCode:{}'.format(len(pole.groupby(['CityName','TownName','VilName'],as_index=False).count()))
print 'after sample amount:{}'.format(len(pole))
#pole.groupby(['CityName','TownName','VilName'],as_index=False).count()[['CityName','TownName','VilName']].to_csv('D:/Users/Qoo/Desktop/pole_before.csv',index=False, encoding='utf-8')


# In[12]:


#clean wrong words
pole.CityName = pole.CityName.replace({u'臺':u'台'},regex=True)
pole.VilName = pole.VilName.replace({u'臺':u'台'},regex=True)
pole.TownName = pole.TownName.replace({u'頭份鎮':u'頭份市'},regex=True)
pole.VilName = pole.VilName.replace({u'磚瑤里':u'磚磘里'},regex=True)
pole.VilName = pole.VilName.replace({u'部下村':u'廍下村'},regex=True)
pole.VilName = pole.VilName.replace({u'回瑤里':u'硘磘里'},regex=True)
pole.VilName = pole.VilName.replace({u'石弄村':u'石硦村'},regex=True)
pole.VilName = pole.VilName.replace({u'鹽館村':u'塩館村'},regex=True)
pole.VilName = pole.VilName.replace({u'瑞峰村':u'瑞峯村'},regex=True)
pole.VilName = pole.VilName.replace({u'部子里':u'廍子里'},regex=True)
pole.VilName = pole.VilName.replace({u'龜殼里':u'龜壳村'},regex=True)
pole.VilName = pole.VilName.replace({u'蔗部里':u'蔗廍里'},regex=True)
pole.VilName = pole.VilName.replace({u'慷榔里':u'槺榔里'},regex=True)
pole.VilName = pole.VilName.replace({u'雙龍里':u'双龍里'},regex=True)
pole.VilName = pole.VilName.replace({u'糖部里':u'糖廍里'},regex=True)
pole.VilName = pole.VilName.replace({u'康榔里':u'槺榔里'},regex=True)
pole.VilName = pole.VilName.replace({u'那拔里':u'𦰡拔里'},regex=True)
pole.VilName = pole.VilName.replace({u'鹽洲里':u'塩洲里'},regex=True)
pole.VilName = pole.VilName.replace({u'鹽行里':u'塩行里'},regex=True)
pole.VilName = pole.VilName.replace({u'石曹里':u'石𥕢里'},regex=True)
pole.VilName = pole.VilName.replace({u'土板村':u'土坂村'},regex=True)
pole.VilName = pole.VilName.replace({u'台板村':u'台坂村'},regex=True)
pole.VilName = pole.VilName.replace({u'里龍里':u'里壠里'},regex=True)
pole.VilName = pole.VilName.replace({u'雙福村':u'双福村'},regex=True)
pole.VilName = pole.VilName.replace({u'文峰村':u'文峯村'},regex=True)
pole.VilName = pole.VilName.replace({u'響林村':u'响林村'},regex=True)
pole.VilName = pole.VilName.replace({u'廈北村':u'厦北村'},regex=True)
pole.VilName = pole.VilName.replace({u'廈南村':u'厦南村'},regex=True)
pole.VilName = pole.VilName.replace({u'涼山村':u'凉山村'},regex=True)
pole.VilName = pole.VilName.replace({u'崎峰村':u'崎峯村'},regex=True)
pole.VilName = pole.VilName.replace({u'大峰里':u'大峯里'},regex=True)
pole.VilName = pole.VilName.replace({u'南館村':u'南舘村'},regex=True)
pole.VilName = pole.VilName.replace({u'埤腳村':u'埤脚村'},regex=True)
pole.VilName = pole.VilName.replace({u'新館村':u'新舘村'},regex=True)
pole.VilName = pole.VilName.replace({u'舊館村':u'舊舘村'},regex=True)
pole.VilName = pole.VilName.replace({u'南磘里':u'南瑤里'},regex=True)
pole.VilName = pole.VilName.replace({u'永館里':u'永舘里'},regex=True)
pole.VilName = pole.VilName.replace({u'上館里':u'上舘里'},regex=True)
pole.VilName = pole.VilName.replace({u'峰廷里':u'峯廷里'},regex=True)
pole.VilName = pole.VilName.replace({u'五峰里':u'五峯里'},regex=True)
pole.VilName = pole.VilName.replace({u'爪峰里':u'爪峯里'},regex=True)
pole.VilName = pole.VilName.replace({u'崙峰里':u'崙峯里'},regex=True)
pole.VilName = pole.VilName.replace({u'峰山里':u'峯山里'},regex=True)
pole.VilName = pole.VilName.replace({u'槍寮里':u'獇寮里'},regex=True)
pole.VilName = pole.VilName.replace({u'濂新里':u'濓新里'},regex=True)
pole.VilName = pole.VilName.replace({u'濂洞里':u'濓洞里'},regex=True)
pole.VilName = pole.VilName.replace({u'崁腳里':u'崁脚里'},regex=True)
pole.VilName = pole.VilName.replace({u'水砌村':u'水磜村'},regex=True)
pole.VilName = pole.VilName.replace({u'雞林里':u'鷄林里'},regex=True)
pole.VilName = pole.VilName.replace({u'果林里':u'菓林里'},regex=True)
pole.VilName = pole.VilName.replace({u'果葉村':u'菓葉村'},regex=True)
pole.VilName = pole.VilName.replace({u'時裡里':u'嵵裡里'},regex=True)
pole.VilName = pole.VilName.replace({u'雙潭村':u'双潭村'},regex=True)
pole.VilName = pole.VilName.replace({u'雙湖村':u'双湖村'},regex=True)
pole.VilName = pole.VilName.replace({u'板里村':u'坂里村'},regex=True)
pole.VilName = pole.VilName.replace({u'柏子村':u'萡子村'},regex=True)
pole.VilName = pole.VilName.replace({u'柏東村':u'萡東村'},regex=True)
pole.VilName = pole.VilName.replace({u'帝埔里':u'坔埔里'},regex=True)
pole.VilName = pole.VilName.replace({u'瓦瑤村':u'瓦磘村'},regex=True)
pole.VilName = pole.VilName.replace({u'瓦瑤里':u'瓦磘里'},regex=True)
pole.VilName = pole.VilName.replace({u'灰瑤里':u'灰磘里'},regex=True)
pole.VilName = pole.VilName.replace({u'部':u'廍'},regex=True)
#
pole.loc[(pole.CityName.str.contains(u'台中市'))&(pole.TownName.str.contains(u'西區'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'台中市'))&(pole.TownName.str.contains(u'西區'))
    ,'VilName'].replace({u'公館里':u'公舘里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'台南市'))&(pole.TownName.str.contains(u'七股區'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'台南市'))&(pole.TownName.str.contains(u'七股區'))
    ,'VilName'].replace({u'鹽埕里':u'塩埕里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'台南市'))&(pole.TownName.str.contains(u'安南區'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'台南市'))&(pole.TownName.str.contains(u'安南區'))
    ,'VilName'].replace({u'鹽田里':u'塩田里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'台南市'))&(pole.TownName.str.contains(u'山上區'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'台南市'))&(pole.TownName.str.contains(u'山上區'))
    ,'VilName'].replace({u'玉峰里':u'玉峯里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'台南市'))&(pole.TownName.str.contains(u'新化區'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'台南市'))&(pole.TownName.str.contains(u'新化區'))
    ,'VilName'].replace({u'山腳里':u'山脚里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'台東縣'))&(pole.TownName.str.contains(u'綠島鄉'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'台東縣'))&(pole.TownName.str.contains(u'綠島鄉'))
    ,'VilName'].replace({u'公館村':u'公舘村'},regex=True)
pole.loc[(pole.CityName.str.contains(u'嘉義縣'))&(pole.TownName.str.contains(u'朴子市'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'嘉義縣'))&(pole.TownName.str.contains(u'朴子市'))
    ,'VilName'].replace({u'雙溪里':u'双溪里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'嘉義縣'))&(pole.TownName.str.contains(u'梅山鄉'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'嘉義縣'))&(pole.TownName.str.contains(u'梅山鄉'))
    ,'VilName'].replace({u'雙溪村':u'双溪村'},regex=True)
pole.loc[(pole.CityName.str.contains(u'新北市'))&(pole.TownName.str.contains(u'板橋區'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'新北市'))&(pole.TownName.str.contains(u'板橋區'))
    ,'VilName'].replace({u'公館里':u'公舘里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'苗栗縣'))&(pole.TownName.str.contains(u'竹南鎮'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'苗栗縣'))&(pole.TownName.str.contains(u'竹南鎮'))
    ,'VilName'].replace({u'公館里':u'公舘里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'雲林縣'))&(pole.TownName.str.contains(u'北港鎮'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'雲林縣'))&(pole.TownName.str.contains(u'北港鎮'))
    ,'VilName'].replace({u'公館里':u'公舘里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'雲林縣'))&(pole.TownName.str.contains(u'西螺鎮'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'雲林縣'))&(pole.TownName.str.contains(u'西螺鎮'))
    ,'VilName'].replace({u'公館里':u'公舘里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'高雄市'))&(pole.TownName.str.contains(u'湖內區'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'高雄市'))&(pole.TownName.str.contains(u'湖內區'))
    ,'VilName'].replace({u'公館里':u'公舘里'},regex=True)
pole.loc[(pole.CityName.str.contains(u'苗栗縣'))&(pole.TownName.str.contains(u'苑裡鎮'))
    ,'VilName'] = pole.loc[(pole.CityName.str.contains(u'苗栗縣'))&(pole.TownName.str.contains(u'苑裡鎮'))
    ,'VilName'].replace({u'山腳里':u'山脚里'},regex=True)


# In[13]:


print 'number of unique VilCode:{}'.format(len(pole.groupby(['CityName','TownName','VilName'],as_index=False).count()))
print 'after sample amount:{}'.format(len(pole))
#pole.groupby(['CityName','TownName','VilName'],as_index=False).count()[['CityName','TownName','VilName']].to_csv('D:/Users/Qoo/Desktop/pole_after.csv',index=False, encoding='utf-8')


# In[14]:


# the number of pole type in village
p1 = pole.groupby(['CityName','TownName','VilName'],as_index=False).agg({'p_type':'nunique'})
p1.columns.values[3] = 'pole_type_counts'

# the number of each type's pole in village
p2 = pole.groupby(['CityName','TownName','VilName','p_type'],as_index=False).count()
p2 = p2.pivot_table(index=['CityName','TownName','VilName'],columns='p_type',values='coordinate')
p2 = p2.reset_index()
p2 = p2.fillna(0)
p2.columns.values[3:13] =['p%s' % s for s in range(1,11)] 

# total number of pole in village
p3 = pole.groupby(['CityName','TownName','VilName'],as_index=False).count()
p3.columns.values[3] = 'pole_counts'
p3 = p3.iloc[:,[0,1,2,3]]

#transform columns value from unicode to str
for data in [p1,p2,p3]:
    for column in ['CityName','TownName','VilName']:
        data[column] =  data[column].str.encode('utf-8')


# In[15]:


df3.CityName = df3.CityName.replace({'臺':'台'},regex=True)
df3.VilName = df3.VilName.replace({'臺':'台'},regex=True)


# In[16]:


#df3.CityName = df3.CityName.replace({'臺':'台'},regex=True)
df3 = pd.merge(df3,p1,how='left',on=['CityName','TownName','VilName'])
df3 = pd.merge(df3,p2,how='left',on=['CityName','TownName','VilName'])
df3 = pd.merge(df3,p3,how='left',on=['CityName','TownName','VilName'])


# In[17]:


#impute missing value
df3 = df3.fillna(0)


# In[18]:


# two typhoons or not
df3['double_kill'] = 0
df3.loc[(df3.typhoon =='NESATANDHAITANG')|(df3.typhoon =='MERANTIANDMALAKAS'),'double_kill'] = 1


# In[19]:


# population density in Taiwan 
# data source: https://data.gov.tw/dataset/8410
pop_files = glob.glob(os.path.join(data_path+'population/','*.csv'))
population = pd.concat(pd.read_csv(d, skiprows=2, nrows=370, names=['Minguo_year','location',
            'people_total','area','population_density'] ) for d in pop_files)
population['CityName'] = population.location.str.slice(0,9)
population['TownName'] = population.location.str.slice(9,)

# clean word
population.CityName = population.CityName.replace({'臺':'台'},regex=True)
population.TownName = population.TownName.replace({'員林鎮':'員林市'},regex=True)
population.TownName = population.TownName.replace({'頭份鎮':'頭份市'},regex=True)

# merge data
df3.loc[df3.year == 2017,'Minguo_year'] =105
df3.loc[df3.year == 2016,'Minguo_year'] =105
df3.loc[df3.year == 2015,'Minguo_year'] =104
df3.loc[df3.year == 2014,'Minguo_year'] =103
df3.loc[df3.year == 2013,'Minguo_year'] =102
df3 = pd.merge(df3, population, how='left',on=['CityName','TownName','Minguo_year'] )


# In[20]:


df3.to_csv('D:/Users/Qoo/Desktop/df.csv',index=False, encoding='utf-8')

