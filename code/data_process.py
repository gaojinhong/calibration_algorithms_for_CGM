# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:04:33 2024

@author: hilahun
"""
import numpy as np
import pandas as pd
#from warnings import simplefilter
#simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

cgm_data = pd.read_excel("../data/measuredvalue.xlsx")

#keep blood, ist, segmentid, measuredat and drop the others   
cgm_data.drop(["rowid", "isig", "insulin_bolus", "carbohydrates", "calibration", 
               "insulin_basal_rate", "id"], axis=1, inplace=True)

#convert dtypes of "measuredat" to datetime
cgm_data["measuredat"] = pd.to_datetime(cgm_data["measuredat"]) 

#group cgm_data by segmentid to explore the data, the data contain 79 subjects,
#the longest sbj data has 1620 rows and smallest sbj has 142 rows
cgm_data_grouped = cgm_data.groupby("segmentid")

len_each_sbj = cgm_data_grouped["segmentid"].count()

#due to the shortest sbj length is 142, then cut the all data to 142 length, 
#and let each segment overlap 10%
#There are some timedeltas(~30) that is not 5 min (min is 6 min, max is 25 min), 
#and the max diff of them in glucose concentr is less than the normals (~2.4 vs 4 mmol/L);
#therefor, here the discrepency is ignored and treat as 5 min.
step = 5
repeat = 142
homo_dataset = pd.DataFrame()
homo_dataset["measuredat"] = np.arange(0, 5*repeat, step)
discount = 125 #let each segment overlap 10%, 125/142 ~90%

for name, entries in cgm_data_grouped:
    size = entries.shape[0]
    inner_repeat = size //repeat
    name = str(name)
    entries_blood = entries["blood"].copy()
    entries_ist = entries["ist"].copy()
    new_index = np.arange(0,142,1)
    for i in range(inner_repeat):
        bloodstr = name + "_" + str(i) + "_" + "blood"
        iststr = name + "_" + str(i) + "_" + "ist"
        start = i * repeat
        stop = i * repeat + repeat
        slice_blood = pd.Series(entries_blood[start: stop].values, name=bloodstr, index=new_index)
        slice_ist = pd.Series(entries_ist[start: stop].values, name=iststr, index=new_index)
        homo_dataset = pd.concat([homo_dataset, slice_blood, slice_ist], axis=1)
        
    if size % repeat > 30:
        bloodstr = name + "_" + str(inner_repeat) + "_" + "blood"
        iststr = name + "_" + str(inner_repeat) + "_" + "ist"
        start = size - repeat
        stop = size
        slice_blood = pd.Series(entries_blood[start: stop].values, name=bloodstr, index=new_index)
        slice_ist = pd.Series(entries_ist[start: stop].values, name=iststr, index=new_index)
        homo_dataset = pd.concat([homo_dataset, slice_blood, slice_ist], axis=1)

      
        
#homo_dataset.to_csv("../data/homo_dataset.csv")



"""
#get the counts of null value, all have values, no null values
null_count = pd.isna(cgm_data).sum(axis=0)


#use for data exploration
for name, entries in cgm_data_grouped:
    print(entries["measuredat"].head(5))
    print(entries["measuredat"].tail(5))


#There are some timedeltas(~30) that is not 5 min (min is 6 min, max is 25 min), 
and the max diff of them in glucose concentr is less than the normals (~2.4 vs 4 mmol/L);
therefor, here the discrepency is ignored and treat as 5 min.
for name, entries in cgm_data_grouped:
    entries_nunique = pd.DataFrame()
    entries_nunique["measuredat"] = entries["measuredat"].diff().dt.total_seconds()
    entries_nunique["blood"] = entries["blood"].diff()
    print(entries_nunique["blood"].max())
    print(entries_nunique[entries_nunique["measuredat"] != 300])

slice_blood = pd.Series(entries_blood[start: stop].rename(bloodstr))
       
homo_dataset = pd.concat([homo_dataset, slice_blood], axis=1)
homo_dataset[bloodstr] = entries_blood[start:stop]
"""