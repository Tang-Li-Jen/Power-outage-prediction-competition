
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os
import glob


# In[2]:


path = 'D:/Users/Qoo/Desktop/taipower/data/'


# In[3]:


# Taiwan power usage structure
# data source:https://data.gov.tw/dataset/38959
df = pd.read_csv(path+ 'df.csv')
deparment_power_usage = pd.read_csv(path + 'deparment_power_usage.csv')
df2 = pd.merge(df,deparment_power_usage,how='left',on='COUNTYNAME')


# In[4]:


# typhoon 
# dara source: http://rdc28.cwb.gov.tw/TDB/ntdb/pageControl/ty_warning
typhoon = pd.read_csv(path + 'typhoon_alert.csv',encoding='big5')

# data manipulation 
i = iter(list(typhoon.duration))
duration = zip(i,i)
typhoon_time = pd.DataFrame(duration, columns=['arrive','leave'])
cols = list(typhoon)
cols.remove('duration')
tp = typhoon.loc[0:len(typhoon):2,cols]
tp = tp.reset_index(drop=True)
tp2 = pd.concat([tp,typhoon_time],axis=1,join_axes=[tp.index])

#typhoon alert time period
tp2.arrive = pd.to_datetime(tp2.arrive)
tp2.leave = pd.to_datetime(tp2.leave)
tp2.year = tp2.arrive.dt.year
mask = (tp2.year >=2014) & (tp2.year<=2017)
tp3 = tp2[mask]


# In[5]:


# import power usage data
# note: There is no data for 2014, so I use 2015 instead
all_files = glob.glob(os.path.join(path+'vil_power/','*.csv'))
p_201406 = pd.read_csv(all_files[0],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])
p_201407 = pd.read_csv(all_files[1],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])
p_201409 = pd.read_csv(all_files[3],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])

p_201507 = pd.read_csv(all_files[1],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])
p_201508 = pd.read_csv(all_files[2],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])
p_201509 = pd.read_csv(all_files[3],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])

p_201607 = pd.read_csv(all_files[4],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])
p_201609 = pd.read_csv(all_files[5],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])

p_201707 = pd.read_csv(all_files[6],encoding='big5',skipfooter=1,usecols=[0,1,2,3,4,5])

# assign year and month
p_201406['year'] = 2014
p_201406['month'] = 6

p_201407['year'] = 2014
p_201407['month'] = 7

p_201409['year'] = 2014
p_201409['month'] = 9

p_201507['year'] = 2015
p_201507['month'] = 7

p_201508['year'] = 2015
p_201508['month'] = 8

p_201509['year'] = 2015
p_201509['month'] = 9

p_201607['year'] = 2016
p_201607['month'] = 7

p_201609['year'] = 2016
p_201609['month'] = 9

p_201707['year'] = 2017
p_201707['month'] = 7


# In[6]:


p = pd.concat([p_201406,p_201407,p_201409,p_201507,p_201508,p_201509,p_201607,p_201609,p_201707],axis=0)


# In[7]:


#data cleaning 
p[u'用電種類'] = p[u'用電種類'].str.replace(u'　',u'')
p2 = p.loc[(p[u'用電種類']== u'1表燈非營業用')|(p[u'用電種類']== u'2表燈營業用'),:]

# rename cols
p2.rename(columns={u'郵遞區號':'z_code',u'行政區':'TownName',u'用電種類':'usage_type',u'用戶數':'household_amount',
          u'契約容量':'contract_amount',u'售電度數(當月)':'monthly_power_sales_amount','year':'p_year','month':'p_month'},inplace=True)
# drop unused cols
p2 = p2.iloc[:,[0,2,3,4,5,6,7]]


# In[8]:


# import Taiwan Town zcode
zcode = pd.read_csv(path+'taiwan_zcode.csv',encoding='big5')


# In[9]:


p3 = pd.merge(p2, zcode, how='left', on='z_code')
p3.CityName = p3.CityName.str.encode('utf-8')
p3.TownName = p3.TownName.str.encode('utf-8')
# impute missing value
p3.loc[p3.TownName=='烏坵鄉','household_amount'] = 0


# In[10]:


# clean data
p3 = p3.loc[(p3.household_amount != '*'),:]
p3 = p3.loc[(p3.household_amount != '**'),:]
p3 = p3.loc[(p3.household_amount != u'＊'),:]
#p3 = p3.loc[(p3.monthly_power_sales_amount != '*'),:]
#p3 = p3.loc[(p3.monthly_power_sales_amount != '**'),:]
#p3 = p3.loc[(p3.monthly_power_sales_amount != u'＊'),:]

p3.contract_amount = p3.contract_amount.astype(float)
p3.monthly_power_sales_amount = p3.monthly_power_sales_amount.astype(float)
p3.household_amount = p3.household_amount.astype(float)


# In[11]:


p3 = p3.pivot_table(index=['CityName','TownName','p_year','p_month','z_code'],columns='usage_type',values=['household_amount','contract_amount','monthly_power_sales_amount']).reset_index()
p3.to_csv(path+'p3.csv',encoding='utf-8')
p3 = pd.read_csv(path+'p3.csv')

p3.p_year = p3.p_year.astype(float)
df3 = pd.merge(df2, p3, how='left', left_on=['CityName','TownName','year','arrive_month'],
              right_on=['CityName','TownName','p_year','p_month'] )
df3.rename(columns={'contract_amount':'non_profit_contract_amount','contract_amount.1':'profit_contract_amount',
                   'monthly_power_sales_amount':'non_profit_monthly_power_sales_amount','monthly_power_sales_amount.1':'profit_monthly_power_sales_amount',
                   'household_amount':'non_profit_household_amount','household_amount.1':'profit_household_amount'},inplace=True)


# In[12]:


df3.non_profit_household_amount = df3.non_profit_household_amount.astype(float)
df3.profit_household_amount = df3.profit_household_amount.astype(float)

df3.non_profit_contract_amount = df3.non_profit_contract_amount.astype(float)
df3.profit_contract_amount = df3.profit_contract_amount.astype(float)

df3.non_profit_monthly_power_sales_amount = df3.non_profit_monthly_power_sales_amount.astype(float)
df3.profit_monthly_power_sales_amount = df3.profit_monthly_power_sales_amount.astype(float)


# In[13]:


df3['sum_contract_amount'] = df3[['non_profit_contract_amount','profit_contract_amount']].apply(sum,axis=1)
df3['sum_household_amount'] = df3[['non_profit_household_amount','profit_household_amount']].apply(sum,axis=1)
df3['sum_monthly_power_sales_amount'] = df3[['non_profit_monthly_power_sales_amount','profit_monthly_power_sales_amount']].apply(sum,axis=1)


# In[14]:


df3.to_csv(path+'df.csv',encoding='utf-8', index=False)

