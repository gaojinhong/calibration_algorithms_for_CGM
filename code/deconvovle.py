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
5 On-line calibration of glucose sensors from the measured current by a time-varying calibration
function and Bayesian priors
"""


import pandas as pd
import numpy as np
from scipy.integrate import quad
from math import exp
from numpy.linalg import inv

data = pd.read_csv("../data/homo_dataset.csv")

#set the convolve function and related parameters
Tau = 16
Cvle_time = 175
Integrate_step = 5
Cvle_scale = Cvle_time/Integrate_step
Gama = 10

def convolve_func(t, tau):
    return 1/tau * exp(-t/tau)

convovle_array = np.zeros(142)


for i in range(int(Cvle_scale+1)):
    t = quad(convolve_func, i*5, (i+1)*5, args=Tau)
    convovle_array[i] = t[0]

convovle_array_flip = np.flip(convovle_array)

G_matrix = np.zeros((142, 142))

for i in range(142):
    line = convovle_array_flip[141-i:142]
    G_matrix[i][0:i+1] = line

"""
Comment: np.sum(G_matrix[3]) ~= 0.713 << 0.85, and np.sum(G_matrix[3]) ~= 0.79 ~=0.8
therefore adjust the sum of each row to ~0.85 before row 4, to reduce the edge effect in 
convolution
"""
G_matrix[3] = G_matrix[3] *(0.85/np.sum(G_matrix[3]))
G_matrix[2] = G_matrix[2] *(0.85/np.sum(G_matrix[2]))
G_matrix[1] = G_matrix[1] *(0.85/np.sum(G_matrix[1]))
G_matrix[0] = G_matrix[0] *(0.85/np.sum(G_matrix[0]))


#F1=I, F2=I-I(k=-1), F3=I-2*I(k=-1)+I(k=-2)
def gen_F_matrix(m_type):
    if int(m_type) == 1:
        return np.eye(142)
    if int(m_type) == 2:
        return np.eye(142) - np.eye(142, k=-1)
    if int(m_type)== 3:
        return np.eye(142) - 2* np.eye(142, k=-1) + np.eye(142, k=-2)
    
#Assume Sigma_v_matrix = I
Sigma_v_matrix = np.eye(142)

#Take F_matrix = F3, Sigma_u_matrix.inverse = (F_matrix.T).dot(F_matrix)
F_matrix = gen_F_matrix(3)  
Sigma_u_matrix_inverse = np.dot(F_matrix.T, F_matrix)

#delta_gama_matrix = [(G.T * (Sigma_v_matrix)**-1 * G + Gama * (Sigma_u_matrix)**-1) **-1 ] * G.T * (Sigma_v_matrix)**-1 
delta_gama_matrix  = inv(((G_matrix.T).dot(np.dot(inv(Sigma_v_matrix), G_matrix)) + Gama * Sigma_u_matrix_inverse)).dot(np.dot(G_matrix.T, inv(Sigma_v_matrix)))






