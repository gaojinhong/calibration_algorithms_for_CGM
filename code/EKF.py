# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:58:35 2024
@author: hilahun

reproduced from literature of "The Extended Kalman Filter for
Continuous Glucose Monitoring"
method comments:
The EKF method heavily depend on initial condition (both initial state and covariance matrix assumation).
In this recomplement, the artificial setting on decay of ks (sensitivy of CGM) dramatically lead 
to catastrophic wrong bld glu output (see the filtered_data, the first half items are similar to groundtruth value,
however the last parts are extreme derived from the groundtruth).
and the initial choice of tau from 6 to 3, impressive improve the output.

may refer to:
https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python/blob/master/11-Extended-Kalman-Filters.ipynb
the implement of the method can be done in a more elegant way (i.e. implement it in a class form and in sympy symbolic express), however, I do not have enough motivation to make it.
"""

import pandas as pd
import numpy as np
from filterpy.kalman import ExtendedKalmanFilter

#get the data only first sample column "1_0_blood" and "1_0_ist"
data = pd.read_csv("../data/homo_dataset.csv")

bld_1_0 = data["1_0_blood"]
ist_1_0 = data["1_0_ist"]

#time step
dt = 5

#CGM filter
sensor_filter = ExtendedKalmanFilter(dim_x = 5, dim_z = 1)

#initial guess
sensor_filter.x = np.array([ist_1_0[0], bld_1_0[0], 3, 0, 0.5]);

#state transition matrix, F
sensor_filter.F = np.eye(5)
sensor_filter.F[0, 0] = np.exp(-dt*sensor_filter.x[2])
sensor_filter.F[0, 1] = 1- np.exp(-dt*sensor_filter.x[2])
sensor_filter.F[0, 2] = (sensor_filter.x[1] -sensor_filter.x[0])*(1- np.exp(-dt*sensor_filter.x[2]))/sensor_filter.x[2]
sensor_filter.F[0, 3] = (-1 + sensor_filter.x[2] *dt + np.exp(-dt*sensor_filter.x[2]))/sensor_filter.x[2]
sensor_filter.F[1, 3] = dt

#define Jacobian_matrix for ist_glu measure current and bld_glu
def jacobian_matrix_ist(x):
    return np.array([[x[4], 0, 0, 0, x[0]]])

def jacobian_matrix_bld(x):
    return np.array([[0, 1, 0, 0, 0]])

#define measure function for ist_glu measure current and bld_glu
def measure_ist_glu(x):
    y = x[0]*x[4]
    return y

def measure_bld_glu(x):
    y = x[1]
    return y

#Process noise covariance matrix initialization, Q
sensor_filter.Q = np.array([[1, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0],
                            [0, 0, 0.06, 0, 0],
                            [0, 0, 0, 3, 0],
                            [0, 0, 0, 0, 0.001]])

#two measure noise variance matrix, ist_glu current and bld_glu
#depend on which measurement used, one can change it with sensor_filter.R = ist_glu_variance or bld_glu_variance
ist_glu_variance = np.diag([0.05])
bld_glu_variance = np.diag([0.1])

#covariance matrix of P
sensor_filter.P = np.array([[1, 1, 0, 0, 0],
                            [1, 1, 0, 0, 0],
                            [0, 0, 3, 0, 0],
                            [0, 0, 0, 3, 0],
                            [0, 0, 0, 0, 0.1]])

#process data
filtered_data = np.zeros(142)

for i in range(1, bld_1_0.size):
    measure_ist = ist_1_0[i]
    sensor_filter.update(np.array([measure_ist]), jacobian_matrix_ist, measure_ist_glu)
    filtered_data[i] = sensor_filter.x[1]
    sensor_filter.F[0, 0] = np.exp(-dt*sensor_filter.x[2])
    sensor_filter.F[0, 1] = 1- np.exp(-dt*sensor_filter.x[2])
    sensor_filter.F[0, 2] = (sensor_filter.x[1] -sensor_filter.x[0])*(1- np.exp(-dt*sensor_filter.x[2]))/sensor_filter.x[2]
    sensor_filter.F[0, 3] = (-1 + sensor_filter.x[2] *dt + np.exp(-dt*sensor_filter.x[2]))/sensor_filter.x[2]
    sensor_filter.predict()



"""
#ist_glu means interstitial fluid glucose, bld means blood, tao is the ist/bld tansist constant
#bld_chg_rate is the change bld_glu change rate, ks is the sensor sensitivity
class CGM_model():
    def __init__(self, ist_glu, bld_glu, tao, bld_chg_rate, ks, dt):
        self.ist_glu = ist_glu
        self.bld_glu = bld_glu
        self.tao = tao
        self.bld_chg_rate = bld_chg_rate
        self.ks = ks
        self.dt = dt
        
    def measure(self):
        cgm_sgn = self.ist_glu * self.ks
        bgm_sgn = self.bld_glu
        
        return cgm_sgn, bgm_sgn
"""