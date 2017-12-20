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

path = '/Users/charlie/Desktop/Taipower/data/'
#df3 = pd.read_csv('df_1115_final_2.csv')
df3 = pd.read_csv(path +'df_1117.csv')
df3 = df3.fillna(0)
#split data to train and test
te = df3.loc[(df3.typhoon=='NESATANDHAITANG')|(df3.typhoon=='MEGI'),:]
keep = list(set(df3.index) - set(te.index))
tr = df3.iloc[keep,:]
print(len(te))
print(len(tr))
print(len(df3))


#
var = ['year','type',
       'magnitude', 'hpa', 'wind_speed', 'r7_km', 'r10_km', 'alert_level',
       'arrive_month', 'arrive_hour', 'arrive_weekday',
       'arrive_week','duration_h', 'pole_type_counts', 'p1',
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
       'how_rain_count_rule2', 
       'max_intensityOverDsqrt_time_10000_log2', 'max_day_lt',
       'max_hour_lt', 'tp_service_num', 
       'vil_st_distance', 'd_mean_hr_wsmax', 'd_mean_hr_wsgust',
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
       'sum_household_amount', 'sum_monthly_power_sales_amount']

tr_x = tr.loc[:,var]
tr_y = np.log1p(tr.loc[:,'elect_down'])
te_N = te.loc[te.typhoon =='NESATANDHAITANG', var]
te_M = te.loc[te.typhoon =='MEGI', var]

from sklearn.model_selection import GridSearchCV
from sklearn.datasets import make_friedman1
from sklearn.feature_selection import RFE


from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5)

def TaipowerScore(preds, res):
    labels = res
    score =2*sum([i*j for i,j in zip(preds, labels)])/sum([i**2 + j**2 for i,j in zip(preds, labels)])
    if sum([i**2 + j**2 for i,j in zip(preds, labels)]) == 0.0:
        score = 1
    else:
        score = 2*sum([i*j for i,j in zip(preds, labels)])/sum([i**2 + j**2 for i,j in zip(preds, labels)])
    return score

y_binned = np.ones(len(tr_y))
y_binned[[i for i,j in enumerate(tr_y) if j ==0]] = 0

with open("log1117.txt", "w") as text_file:
    text_file.write('start')

    ## number of variables ex 
    for n in [20,30,40]:

    	## RandomForestRegressor :you can select any model
        rfr = RandomForestRegressor(n_jobs=-1)
        selector = RFE(rfr, n, step=1)
        selector = selector.fit(tr_x,tr_y)

        ## different hyperparameter
        for p in [100,200,300,400]:
            for f in [None,'auto']:

                scores=[]
                scores_rms=[]

                for train_index, test_index in skf.split(tr_x,y_binned):
                    regr = RandomForestRegressor(n_estimators=p,oob_score=True,n_jobs=-1)
                    regr.fit(tr_x.loc[train_index,selector.support_],tr_y[train_index])
                    pred = regr.predict(tr_x.loc[test_index,selector.support_])
                    scores_rms.append(np.sqrt(np.mean((pred-tr_y[test_index])**2)))
                    scores.append(TaipowerScore(pred,tr_y[test_index]))

                text_file.write("n_feature={}".format(n))
                text_file.write("\n")
                text_file.write("n_estimators={}".format(p))
                text_file.write("\n")
                text_file.write("max_feature={}".format(f))
                text_file.write("\n")
                text_file.write("score_sd={}".format(np.std(scores)))
                text_file.write("\n")
                text_file.write("score_raw={}".format(scores))
                text_file.write("\n")
                text_file.write("score={}".format(sum(scores)/len(scores)))
                text_file.write("\n")
                text_file.write("scores_rms_sd={}".format(np.std(scores_rms)))
                text_file.write("\n")
                text_file.write("scores_rms_raw={}".format(scores_rms))
                text_file.write("\n")
                text_file.write("scores_rms={}".format(sum(scores_rms)/len(scores_rms)))
                text_file.write("\n")
            print 'number of p: {}'.format(p)
        print 'number of n: {}'.format(n)            