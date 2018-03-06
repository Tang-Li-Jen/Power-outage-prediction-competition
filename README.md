# Power-outage-prediction-competition
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
### Feature Engineering
Due to lack of explantory variables, we had to collect features from government open data. All the open data we used are listed in reference. We just show the **key datasets and features** below:
1. Typhoon Track

2. Wind
3. Rainfall
4. Utility Pole
### Modeling
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
