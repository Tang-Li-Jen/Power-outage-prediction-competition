import numpy as np
import pandas as pd
import os
import glob
import xml.etree.ElementTree as ET
from sklearn.ensemble import RandomForestRegressor
import lightgbm as lgb
from sklearn.model_selection import train_test_split

from mlxtend.regressor import StackingCVRegressor
from mlxtend.feature_selection import ColumnSelector
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.model_selection import GridSearchCV


df3 = pd.read_csv('/Users/charlie/Desktop/Taipower/data/df_1120.csv')
#split data to train and test
te = df3.loc[(df3.typhoon=='NESATANDHAITANG')|(df3.typhoon=='MEGI'),:]
keep = list(set(df3.index) - set(te.index))
tr = df3.iloc[keep,:]
print(len(te))
print(len(tr))
print(len(df3))

var =['year', 'type',
       'magnitude', 'hpa', 'wind_speed', 'r7_km', 'r10_km', 'alert_level',
       'arrive_month', 'arrive_hour', 'arrive_weekday',
       'arrive_week',  'duration_h', 'pole_type_counts', 'p1',
       'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10',
       'pole_counts', 'double_kill', 
       'people_total', 'area', 'population_density',
       'mean_accu_hour_rain', 'mean_accu_day_rain', 'accu_rain',
       'heavy_rain_count_rule1', 'heavy_rain_count_rule2',
       'how_rain_count_rule1', 'big_how_rain_count',
       'big_big_how_rain_count', 'max_hour_accu_rain', 'max_day_accu_rain',
       'total_wind_direction_m', 'total_wind_direction_g', 'mean_WSDmax',
       'max_WSDmax', 'mean_WSDgust', 'max_WSDgust', 'landslide_alert',
       'greater_than_five', 'one_to_four', 'none', 'river_num',
       'region_cluster', 'mean_accu_3hour_rain', 'mean_accu_6hour_rain',
       'mean_accu_12hour_rain', 'max_accu_3hour_rain',
       'max_accu_6hour_rain', 'max_accu_12hour_rain',
       'how_rain_count_rule2', 'max_intensityOverDsqrt', 
       'max_intensityOverDsqrt_time_10000_log2', 'max_day_lt',
       'max_hour_lt', 'tp_service_num', 
        'd_mean_hr_wsmax', 'd_mean_hr_wsgust',
       'd_max_hr_wsmax', 'd_max_hr_wsgust', 'd_total_daily_sum_WSMax',
       'd_total_daily_sum_WSGust', 'WDM_1', 'WDM_2', 'WDM_4', 'WDM_5',
       'WDM_6', 'WDM_8', 'WDM_9', 'WDM_10', 'WDM_12', 'WDM_13', 'WDM_14',
       'WDM_16', 'WDG_1', 'WDG_2', 'WDG_4', 'WDG_5', 'WDG_6', 'WDG_8',
       'WDG_9', 'WDG_10', 'WDG_12', 'WDG_13', 'WDG_14', 'WDG_16',
       'accu_lt_num', 'mean_hour_lt_num', 'mean_day_lt_num',
       'max_hour_lt_num', 'max_day_lt_num', 'abs_max_lt', 'mean_hr_wsmax',
       'mean_hr_wsgust', 'max_hr_wsmax', 'max_hr_wsgust',
       'total_daily_sum_WSMax', 'total_daily_sum_WSGust', 'mean_1D_wm',
       'mean_2D_wm', 'mean_3D_wm', 'mean_5D_wm', 'mean_6D_wm',
       'mean_8D_wm', 'mean_1D_wg', 'mean_2D_wg', 'mean_3D_wg',
       'mean_5D_wg', 'mean_6D_wg', 'mean_8D_wg', 'max_1D_wm', 'max_2D_wm',
       'max_3D_wm', 'max_5D_wm', 'max_6D_wm', 'max_8D_wm', 'max_1D_wg',
       'max_2D_wg', 'max_3D_wg', 'max_5D_wg', 'max_6D_wg', 'max_8D_wg',
       'mean_wdmax', 'mean_wdgust', 'aggre_intensity_kx_clip_avg',
       'aggre_intensity_kx_clip_sum', 'max_moment_ratio',
       'max_intensity_kx_clip_value', 'civil_percent', 'service_percent',
       'department_percent', 'industry_percent', 'other_percent',
       'non_profit_contract_amount', 'profit_contract_amount',
       'non_profit_household_amount', 'profit_household_amount',
       'non_profit_monthly_power_sales_amount',
       'profit_monthly_power_sales_amount', 'sum_contract_amount',
       'sum_household_amount', 'sum_monthly_power_sales_amount',
       'pm_c_count', 'pm_t_count', 'pm_v_count']
########## rf
tmp = ['year','type','magnitude','hpa','wind_speed','r7_km','r10_km','alert_level','arrive_month','arrive_hour',
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
cols20 = [i for i,j in enumerate(var) if j in tmp]

pipe1 = make_pipeline(ColumnSelector(cols=tuple(cols20)),
                      RandomForestRegressor(n_estimators=100,n_jobs=-1))

tmp = ['year','type','magnitude','hpa','wind_speed','r7_km','r10_km','alert_level','arrive_month','arrive_hour',
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
       'sum_household_amount', 'sum_monthly_power_sales_amount',
      'civil_percent', 'service_percent',
       'department_percent', 'industry_percent', 'other_percent']
cols50 = [i for i,j in enumerate(var) if j in tmp]

pipe2 = make_pipeline(ColumnSelector(cols=tuple(cols50)),
                      RandomForestRegressor(n_estimators=100,n_jobs=-1))

tmp = ['year','type','magnitude','hpa','wind_speed','r7_km','r10_km','alert_level','arrive_month','arrive_hour',
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
       'sum_household_amount', 'sum_monthly_power_sales_amount',
      'pm_c_count', 'pm_t_count', 'pm_v_count']

cols80 = [i for i,j in enumerate(var) if j in tmp]

pipe3 = make_pipeline(ColumnSelector(cols=tuple(cols80)),
                      RandomForestRegressor(n_estimators=100,n_jobs=-1))

tmp = ['year','type','magnitude','hpa','wind_speed','r7_km','r10_km','alert_level','arrive_month','arrive_hour',
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
       'sum_household_amount', 'sum_monthly_power_sales_amount',
      'pm_c_count', 'pm_t_count', 'pm_v_count',
      'aggre_intensity_kx_clip_avg',
       'aggre_intensity_kx_clip_sum', 'max_moment_ratio',
       'max_intensity_kx_clip_value']
cols100 = [i for i,j in enumerate(var) if j in tmp]

pipe4 = make_pipeline(ColumnSelector(cols=tuple(cols100)),
                      RandomForestRegressor(n_estimators=100,n_jobs=-1))

#cols137 = [i for i,j in enumerate(var) if j in var]

#pipe5 = make_pipeline(ColumnSelector(cols=tuple(cols137)),
#                      RandomForestRegressor(n_estimators=100,n_jobs=-1))


lasso = Lasso()

lasso = Lasso(alpha=0.5)
stack1 = StackingCVRegressor(regressors=(pipe1, pipe2,pipe3,pipe4), 
                        use_features_in_secondary=True,
                        meta_regressor=lasso)
tr_x = tr.loc[:,var]
#tr_x2 = tr.loc[:,var2]
tr_y = tr.loc[:,'elect_down']
#tr_y2 = tr.loc[:,'square_elect_down']
te_N = te.loc[te.typhoon =='NESATANDHAITANG', var]
te_M = te.loc[te.typhoon =='MEGI', var]
stack1.fit(tr_x.values, tr_y.values)

Nes = stack.predict(te_N.values)
Meg = stack.predict(te_M.values)

test = pd.read_csv('/Users/charlie/Desktop/Taipower/data/submit.csv')
#test.NesatAndHaitang = Nes *(602539/2471910.1150000058)
#test.Megi = Meg *(4180000/3816284.0750000146)
test.NesatAndHaitang = Nes
test.Megi = Meg
test.to_csv('/Users/charlie/Desktop/Taipower/data/sub_1120.csv',index=False)