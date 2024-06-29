# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 16:33:54 2024

@author: hilahun
"""

import pandas as pd
import numpy as np
from symfit import Parameter, Variable, Fit

#get the data only first sample column "1_0_blood" and "1_0_ist, and align them into
#the formation that ar need
data = pd.read_csv("../data/homo_dataset.csv")

bld_1_0 = data["1_0_blood"]
ist_1_0 = data["1_0_ist"]


row_index = np.arange(0, 139)
df_for_armodel = pd.DataFrame(columns=['u1','u2','u3','y1','y2','y3','y4'], index=row_index)

for i in range(row_index.size):
    df_for_armodel.iloc[i, 0:3] = ist_1_0[i+1:i+4].values
    df_for_armodel.iloc[i, 3:7] = bld_1_0[i:i+4].values


error_item = np.random.normal(0, 1e-9, 139)

"""model1: AR(box-jenkins models) using symfit module"""
#define parameters and variables
b0 = Parameter("b0")
b1 = Parameter("b1")
b2 = Parameter("b2")
f1 = Parameter("f1")
f2 = Parameter("f2")
f3 = Parameter("f3")
c1 = Parameter("c1")
c2 = Parameter("c2")
c3 = Parameter("c3")
d1 = Parameter("d1")
d2 = Parameter("d2")
d3 = Parameter("d3")

u1 = Variable("u1")
u2 = Variable("u2")
u3 = Variable("u3")
y1 = Variable("y1")
y2 = Variable("y2")
y3 = Variable("y3")
y4 = Variable("y4")
error = Variable("error")


#difine AR model
model_dict = {y4: (b0*u3+b1*u2+b2*u1)/(1+f1*y3/y4+f2*y2/y4+f3*y1/y4)+ \
              (1+c1*y3/y4+c2*y2/y4+c3*y1/y4)*error/(1+d1*y3/y4+d2*y2/y4+d3*y1/y4)}


"""AR(box-jenkins models) using lmfit module"""


"""AR(box-jenkins models) using scipy and sympy module"""
