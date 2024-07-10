# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 12:49:35 2024

@author: hilahun
"""

import pandas as pd
import numpy as np
from numpy.linalg import inv
from scipy.linalg import fractional_matrix_power
import matplotlib.pyplot as plt
from deconvution_method import get_G_matrix, gen_F_matrix

#data = pd.read_csv("../data/homo_dataset.csv")
#bld = data["225_0_blood"]
#ist = data["225_0_ist"]


data = pd.read_csv("../data/measuredvalue_drop_datetime.csv", index_col=("segmentid"))
data_grouped = data.groupby("segmentid")

selected_data = data_grouped.get_group(288)

bld = selected_data["blood"]
ist = selected_data["ist"]

row_len = bld.size
limit_size = 400

if limit_size:
    bld = selected_data["blood"][0:limit_size]
    ist = selected_data["ist"][0:limit_size]
    row_len = limit_size

#set the convolve function and related parameters
Tau = 16
Cvle_time = 175
Integrate_step = 5
Gama = 0.08

G_matrix = get_G_matrix(Tau, row_len)
#Assume Sigma_v_matrix = I
Sigma_v_matrix = np.eye(row_len)

#Take F_matrix = F3, Sigma_u_matrix.inverse = (F_matrix.T).dot(F_matrix)
F_matrix = gen_F_matrix(3, row_len)  
Sigma_u_matrix_inverse = np.dot(F_matrix.T, F_matrix)

#delta_gama_matrix = [(G.T * (Sigma_v_matrix)**-1 * G + Gama * (Sigma_u_matrix)**-1) **-1 ] * G.T * (Sigma_v_matrix)**-1 
delta_gama_matrix  = inv((G_matrix.T).dot(np.dot(inv(Sigma_v_matrix), G_matrix)) + Gama * Sigma_u_matrix_inverse).dot(np.dot(G_matrix.T, inv(Sigma_v_matrix)))

#plot the deconvolve data and original data
deconv_ist = delta_gama_matrix.dot(ist)

time_range = np.arange(0, row_len*5, 5)

reconv_ist = G_matrix.dot(deconv_ist)

plt.plot(time_range, deconv_ist, label="deconv_ist")
plt.plot(time_range, bld, label="bld")
plt.plot(time_range, ist, label="ist")
plt.plot(time_range, reconv_ist, label="reconv")
plt.legend()
plt.show()

#Optimize the Gama value
#S(y) = Sigma_v**-1/2 *G  [(G.T * (Sigma_v_matrix)**-1 * G + Gama * (Sigma_u_matrix)**-1) **-1 ] *G.T* Sigma_v**-1/2 
neghalf_pow_sigV = fractional_matrix_power(Sigma_v_matrix, -1/2)

S_matrix_of_gama = np.dot((neghalf_pow_sigV.dot(G_matrix)).dot(inv((G_matrix.T).dot(np.dot(inv(Sigma_v_matrix), G_matrix)) + Gama * Sigma_u_matrix_inverse)), (G_matrix.T).dot(neghalf_pow_sigV))

QvaL_gama = np.trace(S_matrix_of_gama)

residual_gama = ist - reconv_ist
WSSR_gama = np.dot(residual_gama, residual_gama)
WSSU_gama = np.dot(reconv_ist, Sigma_u_matrix_inverse.dot(reconv_ist))

print(WSSR_gama * QvaL_gama /(WSSU_gama *(row_len - QvaL_gama)))
print(f"Gama {Gama}")