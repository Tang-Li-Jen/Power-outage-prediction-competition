# Power-outage-prediction-competition
![image](https://github.com/Tang-Li-Jen/Power-outage-prediction-competition/blob/master/images/power_outage_wallpaper.PNG)
The competition was held by **DSP** and **Taipower** in Taiwan. I teamed up with **Lawrencesiao**. He is my best teammate and mentor in data science. He helped me do feature engineering and fine-tune predictive model to reach the top rank. If you have any interest, you can see his github here(https://github.com/lawrencesiao)
## Problem Statement
For a long time, Taiwan often suffers from typhoons which cause lots of power outages. For instance, **SOUDELOR(2015/08)**, the most harmful typhoon, bring about **4500 thousands** power outages in Taiwan. In light of this, Building **resilient cities** to prevent future damages becomes more and more important. Therefore, The competition hoped contestants can make accurate and applicable predictive models to help Taiwan get well-prepared in advance.  
**Given the typhoon-caused power outages data from 2014 to 2016, predict the numbers of power outages caused by** ***MEGI(2016)*** and ***NESAT&HAITANG(2017)*** **typhoon.**
## Dataset
Train dataset includes 8 historic typhoons(2014-2016) and their damages(power outages) on each Taiwan Village.  
![image](https://github.com/Tang-Li-Jen/Power-outage-prediction-competition/blob/master/images/train.PNG)  
We aim to predict the power outages caused by **MEGI** and **NESAT&HAITANG** typhoon in test dataset(initialized with 0).  
![image](https://github.com/Tang-Li-Jen/Power-outage-prediction-competition/blob/master/images/test.PNG)
## Timeline
Starts at: Sep 20 2017  
Closed on: Nov 20 2017
## Measure
Accuracy based on **Morisita-Horn similarity index**
## Method
### Data Collecting
Due to lack of explanatory variables, we had to collect features from government open data. We thought the causes of power outages are mainly from the falling down of utility poles. Therefore, not only the typhoon intensity itself, we also collect data which strongly related to this cause. All the open data we used are listed in reference, but we just mentioned the **key datasets and features** below. 
### Feature Engineering
1. **Typhoon Track**  
The intensity of typhoon changed along time.So we created important feature to explain the influence of typhoon on each village from physics insight. The metric is calculated by "maximum typhoon intensity adjusted by square distance between village and typhoon".
2. **Wind**  
Considering that strong wind could blow down the utility poles, we collected hourly wind direction and speed data from regional observation stations for each typhoons. We created max, min, mean, etc. attributes to explain the influence of wind on villages from hour,day to whole typhoon period level.
3. **Rainfall**  
Considering that heavy rain might damage the utility poles, we collected hourly accumulated rainfall data from regional observation stations for each typhoons. Not only max, min, mean, etc. distribution-related attributes, we also created features based on Center Weather Bureau's rainfall standard to explain the influence of rainfall on villages from hour,day to whole typhoon period level.
4. **Utility Pole**  
We considered the numbers of utility poles and their types are important. The former implicitly indicated the potential power outages number and the latter revealed what kinds of utility pole are vulnerable. Therefore, we created total utility pole numbers and the numbers of each types to explain the influence of utility poles.
5. **Geo-demographic**  
We thought population density and structure of power usage are highly correlated to power outages. So we use them to explain between-villages difference.
### Modeling
Power outages didn't happen all the times in villages, so we had to deal with this imbalance data problem carefully. We used **random forest regressor** with **stratified cross-validation** method to balance the data(the percentage of villages suffering power outages) in each validation set and determine the best hyper-parameters. 
## Result
We are team **下次再加油** and got 6th prize in leaderboard  
![image](https://github.com/Tang-Li-Jen/Power-outage-prediction-competition/blob/master/images/rank.PNG)

## Improvement
1. We should do more effort on **data imputation**, especially for the numbers of utility poles in Taiwan villages. Because of lack of utility pole data in few villages, We can consider using similar grid imputation like KNN to impute value based on demographic or other features.
2. We found large performance difference between random forest and xgboost model, which indicated **variance-bias trade-off**. We should fine-tune two kind of models to make stacking model outperform any sigle one.
3. We used rainfall and wind data from 33 regional observation stations. Maybe adding extra **510 automated observation stations** can make the model fit better.
4. Due to wind and rainfall data recorded by observation stations, I assigned one observation station to each village based on **'the shortest Euclidean distance'**, which I represented villages' coordinates by their center coordinates. I think there may be more appropriate methods to do it and get better results.
## Reference
1. DSP Competition Website:https://dc.dsp.im/main/content/Typhoon-caused-Power-Outages-Prediction-Challenge
2. Typhoon Alert: http://rdc28.cwb.gov.tw/TDB/ntdb/pageControl/ty_warning
3. Typhoon Wind: http://rdc28.cwb.gov.tw/TDB/ntdb/pageControl/windsearch
4. Typhoon Rainfall: http://rdc28.cwb.gov.tw/TDB/ntdb/pageControl/rain
5. Typhoon Track: http://rdc28.cwb.gov.tw/TDB/ctrl_advanced_search
6. Utility Pole: https://data.gov.tw/dataset/33305
7. Village Population Density: https://data.gov.tw/dataset/8410
8. Power Usage Percentage by Household, Industries, etc.: https://data.gov.tw/dataset/38959
9. Power Usage by Villages: https://data.gov.tw/dataset/14135
10. Landslide alert: https://246.swcb.gov.tw/OpenData.aspx
11. Lighting: https://data.gov.tw/dataset/9712
