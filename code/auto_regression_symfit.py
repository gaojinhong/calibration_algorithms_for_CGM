# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 16:33:54 2024

@author: hilahun

comment 
reference:
1 https://ch.mathworks.com/help/ident/ug/what-are-polynomial-models.html
2 Real-Time Glucose Estimation Algorithm for Continuous Glucose Monitoring Using Autoregressive Models
"""

import pandas as pd
import numpy as np
from symfit import Parameter, Variable, Fit

#get the data only first sample column "1_0_blood" and "1_0_ist, and align them into
#the formation that ar need
data = pd.read_csv("../data/homo_dataset.csv")

bld_1_0 = data["41_0_blood"]
ist_1_0 = data["41_0_ist"]

bld_24_0 = data["24_0_blood"]
ist_24_0 = data["24_0_ist"]

row_index = np.arange(0, 139)
df_for_armodel = pd.DataFrame(columns=['u1','u2','u3','y1','y2','y3','y4'], index=row_index)

for i in range(row_index.size):
    df_for_armodel.iloc[i, 0:3] = ist_1_0[i+1:i+4].values
    df_for_armodel.iloc[i, 3:7] = bld_1_0[i:i+4].values

df_for_armodel = df_for_armodel.astype("float64")

error_item = np.random.normal(0, 1e-10, 139).astype("float64")

"""model1: AR(box-jenkins models) using symfit module"""
#define parameters and variables
b0 = Parameter("b0", value=0, min=-5, max=5)
b1 = Parameter("b1", value=0, min=-5, max=5)
b2 = Parameter("b2", value=0, min=-5, max=5)
f1 = Parameter("f1", value=0, min=-15, max=15)
f2 = Parameter("f2", value=0, min=-15, max=15)
f3 = Parameter("f3", value=0, min=-15, max=15)
c1 = Parameter("c1", value=0, min=-15, max=15)
c2 = Parameter("c2", value=0, min=-15, max=15)
c3 = Parameter("c3", value=0, min=-15, max=15)
d1 = Parameter("d1", value=0, min=-15, max=15)
d2 = Parameter("d2", value=0, min=-15, max=15)
d3 = Parameter("d3", value=0, min=-15, max=15)

u1 = Variable("u1")
u2 = Variable("u2")
u3 = Variable("u3")
y1 = Variable("y1")
y2 = Variable("y2")
y3 = Variable("y3")
y4 = Variable("y4")
error = Variable("error")
y=Variable("y")


#difine AR model
model_dict = {y: (b0*u3+b1*u2+b2*u1)/(1+f1*y3/y4+f2*y2/y4+f3*y1/y4)+ \
              (1+c1*y3/y4+c2*y2/y4+c3*y1/y4)*error/(1+d1*y3/y4+d2*y2/y4+d3*y1/y4)}

fit = Fit(model_dict, u1=df_for_armodel["u1"].to_numpy(), u2=df_for_armodel["u2"].to_numpy(),\
          u3=df_for_armodel["u3"].to_numpy(), y1=df_for_armodel["y1"].to_numpy(), y2=df_for_armodel["y2"].to_numpy(), \
              y3=df_for_armodel["y3"].to_numpy(), y4=df_for_armodel["y4"].to_numpy(), error=error_item, \
                  y=df_for_armodel["y4"].to_numpy())
    
fit_result = fit.execute()

print(fit_result)



"""AR(box-jenkins models) using scipy and sympy module"""



