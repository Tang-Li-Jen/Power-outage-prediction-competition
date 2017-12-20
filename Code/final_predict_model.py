
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os
import glob
import xml.etree.ElementTree as ET
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold, train_test_split
import xgboost as xgb
from sklearn import linear_model
from math import sqrt
import lightgbm as lgb 
import catboost as ctb
import matplotlib.pyplot as plt
from tabulate import tabulate
from sklearn.decomposition import PCA


# In[2]:


data_path = '/Users/charlie/Desktop/Taipower/data/'


# In[3]:


df3 = pd.read_csv(data_path +'df_1120.csv')


# In[4]:


# find missing value and impute
print df3.isnull().any()[df3.isnull().any() ==True]
df3 =  df3.fillna(0)


# In[5]:


# dependent variable transform
#df3['y1'] = df3['elect_down']+1
#df3['log_elect_down'] = np.log(df3.y1.values)
#df3['square_elect_down'] = np.square(df3.elect_down)
#df3.loc[df3.r10_km > 0 ,'r10_km_y'] =1
#df3.loc[df3.r10_km == 0 ,'r10_km_y'] =0


# In[6]:


#split data to train and test
te = df3.loc[(df3.typhoon=='NESATANDHAITANG')|(df3.typhoon=='MEGI'),:]
keep = list(set(df3.index) - set(te.index))
tr = df3.iloc[keep,:]
print len(te)
print len(tr)
print len(df3)


# In[7]:


#best model variable
var1 = ['year','type','magnitude','hpa','wind_speed','r7_km','r10_km','alert_level','arrive_month','arrive_hour',
       'arrive_weekday','arrive_week','duration_h','pole_type_counts',
 'p1', 'p2', 'p3','p4','p5','p6','p7','p8','p9', 'p10',
       'pole_counts','double_kill', 'people_total','area','population_density',
            'mean_accu_hour_rain', 'mean_accu_day_rain', 'accu_rain',
       'heavy_rain_count_rule1', 'heavy_rain_count_rule2',
       'how_rain_count_rule1', 'big_how_rain_count',
       'big_big_how_rain_count','mean_hr_wsmax', 'mean_hr_wsgust', 'max_hr_wsmax', 'max_hr_wsgust',
      'region_cluster','max_intensityOverDsqrt_time_10000_log2',
      'non_profit_contract_amount', 'profit_contract_amount',
       'non_profit_household_amount', 'profit_household_amount',
       'non_profit_monthly_power_sales_amount',
       'profit_monthly_power_sales_amount', 'sum_contract_amount',
       'sum_household_amount', 'sum_monthly_power_sales_amount']


# In[8]:


# train data
tr_x = tr.loc[:,var1]
tr_y = tr.loc[:,'elect_down']
# test data
te_N = te.loc[te.typhoon =='NESATANDHAITANG', var1]
te_M = te.loc[te.typhoon =='MEGI', var1]

print len(tr_x) , len(tr_y)
print len(te_N) , len(te_M)


# In[9]:


rf = RandomForestRegressor(n_estimators=100, random_state=1992, oob_score=True)
rf.fit(tr_x,tr_y)
headers = ["name", "score"]
values = sorted(zip(tr_x.columns, rf.feature_importances_), key=lambda x: x[1] * -1)
print(tabulate(values, headers, tablefmt="plain"))


# In[10]:


rf.oob_score_


# In[11]:


Nes = rf.predict(te_N)
Meg = rf.predict(te_M)
test = pd.read_csv(data_path+ 'submit.csv')
test.NesatAndHaitang = Nes
test.Megi = Meg
test.to_csv(data_path+ 'sub4.csv',index=False)
print len(Nes)
print len(Meg)


# In[12]:


test.describe()

