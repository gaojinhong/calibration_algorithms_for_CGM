# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 08:32:53 2024

@author: hilahun
reference:
1 Nonparametric Input Estimation in Physiological Systems: Problems, Methods, and Case Studies 
2 Toward Calibration-Free Continuous Glucose Monitoring Sensors: Bayesian Calibration Approach Applied
to Next-Generation Dexcom Technology
3 Reduction of Blood Glucose Measurements to Calibrate Subcutaneous Glucose Sensors: a
Bayesian Multi-day Framework
4 On-line calibration of glucose sensors from the measured current by a time-varying calibration
function and Bayesian priors
5 Predicting Subcutaneous Glucose Concentration in Humans: Data-Driven Glucose Modeling
"""


import pandas as pd
import numpy as np
from scipy.integrate import quad
from math import exp
from numpy.linalg import inv
from scipy.linalg import fractional_matrix_power
import matplotlib.pyplot as plt

data = pd.read_csv("../data/homo_dataset.csv")
bld_1_0 = data["225_0_blood"]
ist_1_0 = data["225_0_ist"]

row_len = bld_1_0.size

#set the convolve function and related parameters
Tau = 16
Cvle_time = 175
Integrate_step = 5
Cvle_scale = Cvle_time/Integrate_step
Gama = 0.15

def convolve_func(t, tau):
    return 1/tau * exp(-t/tau)

convovle_array = np.zeros(row_len)


for i in range(int(Cvle_scale+1)):
    t = quad(convolve_func, i*5, (i+1)*5, args=Tau)
    convovle_array[i] = t[0]

convovle_array_flip = np.flip(convovle_array)

G_matrix = np.zeros((row_len, row_len))

for i in range(row_len):
    line = convovle_array_flip[row_len-i-1:row_len]
    G_matrix[i][0:i+1] = line

"""
Comment: np.sum(G_matrix[3]) ~= 0.713 << 0.85, and np.sum(G_matrix[3]) ~= 0.79 ~=0.8
therefore adjust the sum of each row to ~0.85 before row 4, to reduce the edge effect in 
convolution
"""
G_matrix[3] = G_matrix[4] *(0.95/np.sum(G_matrix[4]))
G_matrix[3] = G_matrix[3] *(0.95/np.sum(G_matrix[3]))
G_matrix[2] = G_matrix[2] *(0.95/np.sum(G_matrix[2]))
G_matrix[1] = G_matrix[1] *(0.95/np.sum(G_matrix[1]))
G_matrix[0] = G_matrix[0] *(0.95/np.sum(G_matrix[0]))


#F1=I, F2=I-I(k=-1), F3=I-2*I(k=-1)+I(k=-2)
def gen_F_matrix(m_type):
    if int(m_type) == 1:
        return np.eye(row_len)
    if int(m_type) == 2:
        return np.eye(row_len) - np.eye(row_len, k=-1)
    if int(m_type)== 3:
        return np.eye(row_len) - 2* np.eye(row_len, k=-1) + np.eye(row_len, k=-2)
    
#Assume Sigma_v_matrix = I
Sigma_v_matrix = np.eye(row_len)

#Take F_matrix = F3, Sigma_u_matrix.inverse = (F_matrix.T).dot(F_matrix)
F_matrix = gen_F_matrix(3)  
Sigma_u_matrix_inverse = np.dot(F_matrix.T, F_matrix)

#delta_gama_matrix = [(G.T * (Sigma_v_matrix)**-1 * G + Gama * (Sigma_u_matrix)**-1) **-1 ] * G.T * (Sigma_v_matrix)**-1 
delta_gama_matrix  = inv(((G_matrix.T).dot(np.dot(inv(Sigma_v_matrix), G_matrix)) + Gama * Sigma_u_matrix_inverse)).dot(np.dot(G_matrix.T, inv(Sigma_v_matrix)))

#plot the deconvolve data and original data
deconv_ist = delta_gama_matrix.dot(ist_1_0)

time_range = np.arange(0, row_len*5, 5)

reconv_ist = G_matrix.dot(deconv_ist)

plt.plot(time_range, deconv_ist, label="deconv_ist")
plt.plot(time_range, bld_1_0, label="bld")
plt.plot(time_range, ist_1_0, label="ist")
plt.plot(time_range, reconv_ist, label="reconv")
plt.legend()
plt.show()

#Optimize the Gama value
#S(y) = Sigma_v**-1/2 *G  [(G.T * (Sigma_v_matrix)**-1 * G + Gama * (Sigma_u_matrix)**-1) **-1 ] *G.T* Sigma_v**-1/2 
neghalf_pow_sigV = fractional_matrix_power(Sigma_v_matrix, -1/2)

S_matrix_of_gama = np.dot((neghalf_pow_sigV.dot(G_matrix)).dot(inv((G_matrix.T).dot(np.dot(inv(Sigma_v_matrix), G_matrix)) + Gama * Sigma_u_matrix_inverse)), (G_matrix.T).dot(neghalf_pow_sigV))

QvaL_gama = np.trace(S_matrix_of_gama)

residual_gama = ist_1_0 - reconv_ist
WSSR_gama = np.dot(residual_gama, residual_gama)
WSSU_gama = np.dot(reconv_ist, Sigma_u_matrix_inverse.dot(reconv_ist))

print(WSSR_gama * QvaL_gama /(WSSU_gama *(row_len - QvaL_gama)))
print(f"Gama {Gama}")
