# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 08:55:56 2024

@author: hilahun
comment 
reference:
1 https://ch.mathworks.com/help/ident/ug/what-are-polynomial-models.html
2 Real-Time Glucose Estimation Algorithm for Continuous Glucose Monitoring Using Autoregressive Models
"""

import pandas as pd
import numpy as np
from lmfit import Minimizer, Parameters, report_fit

#get the data only first sample column "1_0_blood" and "1_0_ist, and align them into
#the formation that ar need
data = pd.read_csv("../data/homo_dataset.csv")

bld_1_0 = data["41_0_blood"]
ist_1_0 = data["41_0_ist"]

row_index = np.arange(0, 139)
df_for_armodel = pd.DataFrame(columns=['u1','u2','u3','y1','y2','y3','y4'], index=row_index)

for i in range(row_index.size):
    df_for_armodel.iloc[i, 0:3] = ist_1_0[i+1:i+4].values
    df_for_armodel.iloc[i, 3:7] = bld_1_0[i:i+4].values

df_for_armodel = df_for_armodel.astype("float64")

error_item = np.random.normal(0, 1e-6, 139).astype("float64")
u1=df_for_armodel["u1"].to_numpy()
u2=df_for_armodel["u2"].to_numpy()
u3=df_for_armodel["u3"].to_numpy()
y1=df_for_armodel["y1"].to_numpy()
y2=df_for_armodel["y2"].to_numpy()
y3=df_for_armodel["y3"].to_numpy()
y4=df_for_armodel["y4"].to_numpy()
y=df_for_armodel["y4"].to_numpy()

"""AR(box-jenkins models) using lmfit module"""
def AR_redisual_model(params, u1, u2, u3, y1, y2, y3, y4, disturb, y):
    b0 = params["b0"]
    b1 = params["b1"]
    b2 = params["b2"]
    f1 = params["f1"]
    f2 = params["f2"]
    f3 = params["f3"]
    c1 = params["c1"]
    c2 = params["c2"]
    c3 = params["c3"]
    d1 = params["d1"]
    d2 = params["d2"]
    d3 = params["d3"]
    model = (b0*u3+b1*u2+b2*u1)/(1.0+f1*y3/y4+f2*y2/y4+f3*y1/y4)+ \
                  (1.0+c1*y3/y4+c2*y2/y4+c3*y1/y4)*disturb/(1.0+d1*y3/y4+d2*y2/y4+d3*y1/y4)
    return model - y

params = Parameters()
params.add("b0", value=0.2, min=-5, max=5)
params.add("b1", value=0.2, min=-5, max=5)
params.add("b2", value=0.2, min=-5, max=5)
params.add("f1", value=0.0, min=-5, max=5)
params.add("f2", value=0.0, min=-5, max=5)
params.add("f3", value=0.0, min=-5, max=5)
params.add("c1", value=0.0, min=-15, max=15)
params.add("c2", value=0.0, min=-15, max=15)
params.add("c3", value=0.0, min=-15, max=15)
params.add("d1", value=0.0, min=-15, max=15)
params.add("d2", value=0.0, min=-15, max=15)
params.add("d3", value=0.0, min=-15, max=15)

minner = Minimizer(AR_redisual_model, params, fcn_args=(u1, u2, u3, y1, y2, y3, y4, error_item, y))
result = minner.minimize()

report_fit(result)