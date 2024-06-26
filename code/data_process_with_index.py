# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:04:14 2024

@author: hilahun
"""


import pandas as pd
from collections import Counter

#from warnings import simplefilter
#simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

cgm_data = pd.read_csv("../data/measuredvalue_drop_datetime.csv", index_col=("segmentid"))
index_list = cgm_data.index
index_counter = Counter(index_list)


print(index_counter)


"""
cgm_data = pd.read_excel("../data/measuredvalue.xlsx")

#keep blood, ist, segmentid, measuredat and drop the others   
cgm_data.drop(["rowid", "isig", "insulin_bolus", "carbohydrates", "calibration", 
               "insulin_basal_rate", "id"], axis=1, inplace=True)

#convert dtypes of "measuredat" to datetime
cgm_data["measuredat"] = pd.to_datetime(cgm_data["measuredat"]) 

cgm_data.to_csv("../data/measuredvalue_drop_datetime.csv")
"""


