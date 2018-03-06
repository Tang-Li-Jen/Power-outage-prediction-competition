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
## Measure
Accuracy based on **Morisita-Horn similarity index**
## Method
1. Typhoon 
2. Utility Pole
3. Wind
4. Rainfall
5. Typhoon Track
## Result
We are team **下次再加油** and got 6th prize in leaderboard  
![image](https://github.com/Tang-Li-Jen/Power-outage-prediction-competition/blob/master/images/rank.PNG)

## Improvement
1. We should do more effort on **data imputation**, especially for the numbers of utility poles in Taiwan villages. Because of lack of utility pole data in few villages, We can consider using similar grid imputation like KNN to impute value based on demographic or other features.
2. We found large performance difference between random forest and xgboost model, which indicated **variance-bias trade-off**. We should fine-tune two kind of models to make stacking model outperform any sigle one.
3. In feature engineering steps, we can create more features to represent their distributions like std, median, etc.
## Reference
1. DSP Competition Website:https://dc.dsp.im/main/content/Typhoon-caused-Power-Outages-Prediction-Challenge
