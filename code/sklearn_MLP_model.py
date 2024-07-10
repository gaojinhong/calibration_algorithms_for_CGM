# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 11:11:01 2024

@author: hilahun
MLP  model using sklearn lib
"""

from sklearn.neural_network import MLPRegressor
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

fit_dim = 25

def prep_data_for_MLP(name, entries, fit_dim, is_small=True):
    
    bld = entries["blood"].to_numpy()
    ist = entries["ist"].to_numpy()
    
    if is_small:
        iter_time = ist.size//fit_dim - 1
    else:
        iter_time = ist.size - fit_dim - 2
    
    feature_len = fit_dim + 2
  
    fit_data = pd.DataFrame(np.zeros((int(iter_time), feature_len)), columns=["ist"+str(i) for i in range(fit_dim)] + ["date", "bld"])
      
    if is_small:
        for i in range(iter_time):
            fit_data.iloc[i, 0:fit_dim] = ist[fit_dim*i:fit_dim*i+fit_dim]
            fit_data.iloc[i, fit_dim+1] = bld[fit_dim*i+fit_dim]
            fit_data.iloc[i, fit_dim] = (fit_dim*i+fit_dim)//288
            
    else:
        for i in range(iter_time):
            fit_data.iloc[i, 0:fit_dim] = ist[i:i+fit_dim]
            fit_data.iloc[i, fit_dim+1] = bld[i+fit_dim-1]
            fit_data.iloc[i, fit_dim] = i/288
            
    return fit_data

cgm_data = pd.read_csv("../data/measuredvalue_drop_datetime.csv", index_col=("segmentid"))
cgm_data_grouped = cgm_data.groupby("segmentid")

dataset_for_MLP = pd.DataFrame(columns=["ist"+str(i) for i in range(fit_dim)] + ["date", "bld"])

for name, entries in cgm_data_grouped:
    get_data = prep_data_for_MLP(name, entries,fit_dim, is_small=False)
    dataset_for_MLP = pd.concat([dataset_for_MLP, get_data], axis=0)
    
X_train, X_test, y_train, y_test = train_test_split(
    dataset_for_MLP[["ist"+str(i) for i in range(fit_dim)] + ["date"]], dataset_for_MLP['bld'], test_size=0.33, random_state=42)


for i in range(1,3):
    regr = MLPRegressor(hidden_layer_sizes=(fit_dim+1,i), random_state=25, max_iter=1500)
    
    regr.fit(X_train, y_train)
    
    result = regr.predict(X_test)
    
    MARD = np.mean(np.abs(result - y_test)/y_test)
    print(i, MARD)


"""
dataset_for_convlv = pd.read_csv("../data/dataset_for_convlv_lg.csv")

X_train, X_test, y_train, y_test = train_test_split(
    dataset_for_convlv[['bld1', 'bld2', 'bld3', 'bld4', 'bld5', 'bld6', 'bld7',
           'bld8', 'bld9', 'bld10', 'date']], dataset_for_convlv['ist'], test_size=0.33, random_state=42)
"""