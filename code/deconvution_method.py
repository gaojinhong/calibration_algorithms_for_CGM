# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 13:32:28 2024

@author: hilahun
"""

import numpy as np
from scipy.integrate import quad
from math import exp


def convolve_func(t, tau):
    return 1/tau * exp(-t/tau)

"""Cvle_time is the convolution time length, Inter_scale is the time-scale for each integrate 
step, row_len is the data length for (de)convolution, fine_tune_scale for some head terms in data to 
make sum of the G_matrix row equal to the fine_tune_scale, N_fine_tune_term is the num of data to be
adjusted
Comment: np.sum(G_matrix[3]) ~= 0.713 << 0.85, and np.sum(G_matrix[3]) ~= 0.79 ~=0.8
therefore adjust the sum of each row to ~0.85 before row 4, to reduce the edge effect in 
convolution
"""
def get_convolve_array(Tau, row_len, Cvle_time=175, Inte_scale=5):
    convovle_array = np.zeros(row_len)
    
    Cvle_scale = Cvle_time/Inte_scale
    for i in range(int(Cvle_scale+1)):
        t = quad(convolve_func, i*5, (i+1)*5, args=Tau)
        convovle_array[i] = t[0]

    convovle_array_flip = np.flip(convovle_array)
    return convovle_array_flip

def get_G_matrix(Tau, row_len, Cvle_time=175, Inte_scale=5,  fine_tune_scale=0.85, N_fine_tune_term=5):

    convovle_array_flip = get_convolve_array(Tau, row_len, Cvle_time=175, Inte_scale=5)
    
    G_matrix = np.zeros((row_len, row_len))
    
    for i in range(row_len):
        line = convovle_array_flip[row_len-i-1:row_len]
        G_matrix[i][0:i+1] = line

    for i in range(N_fine_tune_term):
        G_matrix[i] = G_matrix[i] *(fine_tune_scale/np.sum(G_matrix[i]))
        
    return G_matrix
 
#F1=I, F2=I-I(k=-1), F3=I-2*I(k=-1)+I(k=-2)
def gen_F_matrix(m_type, row_len):
    if int(m_type) == 1:
        return np.eye(row_len)
    if int(m_type) == 2:
        return np.eye(row_len) - np.eye(row_len, k=-1)
    if int(m_type)== 3:
        return np.eye(row_len) - 2* np.eye(row_len, k=-1) + np.eye(row_len, k=-2)