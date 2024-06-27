# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 16:33:54 2024

@author: hilahun
"""

import pandas as pd
import numpy as np

#get the data only first sample column "1_0_blood" and "1_0_ist"
data = pd.read_csv("../data/homo_dataset.csv")

bld_1_0 = data["1_0_blood"]
ist_1_0 = data["1_0_ist"]