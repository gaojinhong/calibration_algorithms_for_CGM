# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 08:56:35 2024

@author: hilahun

some reference: TYPES OF DRIFT
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.optimize import curve_fit
#from lmfit import Minimizer, Parameters, report_fit
#from math import exp
#import matplotlib.pyplot as plt


def convolve_func_discrete(t, tau):
    t = 1/tau * np.exp(-t/tau)
    return t/np.sum(t)

dataset_for_convlv = pd.read_csv("../data/dataset_for_convlv_lg.csv")

X_train, X_test, y_train, y_test = train_test_split(
    dataset_for_convlv[['bld1', 'bld2', 'bld3', 'bld4', 'bld5', 'bld6', 'bld7',
           'bld8', 'bld9', 'bld10', 'date']], dataset_for_convlv['ist'], test_size=0.33, random_state=42)



#dataset_for_convlv.to_csv("../data/dataset_for_convlv_lg.csv")   
#set the convolve function and related parameters
Tau = 21
Cvle_time = 50
Integrate_step = 5
convlv_seq = np.arange(Cvle_time, 0, -Integrate_step)


def convlv_model_np(x, a, b, c, tau):
    
    x_1 = x[:, 0:10]
    x_2 = x[:, 10]
    
    return a*np.dot(x_1, convolve_func_discrete(convlv_seq, tau)) + b +c*x_2

#intial values are chosen arbitrary
fit_params, fit_covar = curve_fit(convlv_model_np, X_train.to_numpy(), y_train, [1.0, 0.3, 0.05, Tau])

#verify the fitting
c = convlv_model_np(X_test.to_numpy(), *fit_params)

#for predict bld(actually ist glucose concen.)
def predict(y, a, b, c, tau):
    return (y-b-c*tau)/a

predict_arr = predict(y_test.to_numpy(), *fit_params)
res = predict_arr - X_test['bld10'].to_numpy()

#MARD ~7.88%
MARD = np.mean(np.abs(res)/X_test['bld10'].to_numpy())

print(fit_params, MARD, Tau)


"""
#data have been transformed and save, but the code remained for further usages and modifications
def prep_data_for_convlv_fit(name, entries, is_small=True):
    
    bld = entries["blood"].to_numpy()
    ist = entries["ist"].to_numpy()
    
    if is_small:
        iter_time = ist.size//10 - 1
    else:
        iter_time = ist.size-11
  
    
    fit_data = pd.DataFrame(np.zeros((int(iter_time), 13)), columns=["bld1", "bld2", "bld3", "bld4", "bld5", "bld6", 
              "bld7", "bld8", "bld9", "bld10", "date", "ist", "segmentid"])
      
    if is_small:
        for i in range(iter_time):
            fit_data.iloc[i, 0:10] = bld[10*i:10*i+10]
            fit_data.iloc[i, 11] = ist[10*i+10]
            fit_data.iloc[i, 10] = (10*i+10)//288
            fit_data.iloc[i, 12] = name
    else:
        for i in range(iter_time):
            fit_data.iloc[i, 0:10] = bld[i:i+10]
            fit_data.iloc[i, 11] = ist[i+9]
            fit_data.iloc[i, 10] = i//288
            fit_data.iloc[i, 12] = name
    return fit_data

cgm_data = pd.read_csv("../data/measuredvalue_drop_datetime.csv", index_col=("segmentid"))
cgm_data_grouped = cgm_data.groupby("segmentid")

dataset_for_convlv = pd.DataFrame(columns=["bld1", "bld2", "bld3", "bld4", "bld5", "bld6", 
          "bld7", "bld8", "bld9", "bld10", "date", "ist", "segmentid"])

for name, entries in cgm_data_grouped:
    get_data = prep_data_for_convlv_fit(name, entries, True)
    dataset_for_convlv = pd.concat([dataset_for_convlv, get_data], axis=0)
    
    
symfit(do work):
model_dict = {y:a*(np.dot(x, convolve_func(convlv_seq, tau))) + b + c * delta_t}

fit = Fit(model_dict, x=X_train[['bld1', 'bld2', 'bld3', 'bld4', 'bld5', 'bld6', 'bld7',
       'bld8', 'bld9', 'bld10']], delta_t=X_train['date'], y=X_train)


lmfit(work, but tedious):
def tau_exp(t, tau):
    return 1/tau * exp(-t/tau)
    
def convlv_model(params, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, delta_t, y):
    a = params['a']
    b = params['b']
    c = params['c']
    tau = params['tau']
    model = a *(x1*tau_exp(50, tau)+x2*tau_exp(45, tau) + x3*tau_exp(40, tau) \
                 + x4*tau_exp(35, tau)+x5*tau_exp(30, tau) + x6*tau_exp(25, tau) \
                + x7*tau_exp(20, tau)+x8*tau_exp(15, tau) + x9*tau_exp(10, tau) \
                  + x10*tau_exp(5, tau))/(tau_exp(50, tau) + tau_exp(45, tau) + tau_exp(40, tau) \
                               + tau_exp(35, tau) + tau_exp(30, tau) + tau_exp(25, tau) \
                              + tau_exp(20, tau) + tau_exp(15, tau) + tau_exp(10, tau) \
                                + tau_exp(5, tau)) + b + c * delta_t
    return y - model



params = Parameters()
params.add('a', value=1.2)
params.add('b', value=10)
params.add('c', value=-0.44)
params.add('tau', value=Tau)

minner = Minimizer(convlv_model, params, fcn_args=(X_train['bld1'].to_numpy(), X_train['bld2'].to_numpy(), 
                                                   X_train['bld3'].to_numpy(), X_train['bld4'].to_numpy(),
                                                   X_train['bld5'].to_numpy(), X_train['bld6'].to_numpy(),
                                                   X_train['bld7'].to_numpy(), X_train['bld8'].to_numpy(),
                                                   X_train['bld9'].to_numpy(), X_train['bld10'].to_numpy(),
                                                   X_train['date'].to_numpy(), y_train.to_numpy()))
    
    
result = minner.minimize()

report_fit(result)
"""
