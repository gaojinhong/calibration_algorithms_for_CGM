# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:58:35 2024

@author: hilahun
"""

import pandas as pd
from filterpy.kalman import ExtendedKalmanFilter

data = pd.read_csv("../data/homo_dataset.csv")

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

dt = 5

cgm_trace = CGM_model(ist_glu, bld_glu, tao, bld_chg_rate, ks)

#CGM filter
sensor_filter = ExtendedKalmanFilter(dim_x = 5, dim_z = 1)
