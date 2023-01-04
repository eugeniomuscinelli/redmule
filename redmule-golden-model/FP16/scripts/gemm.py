#!/scratch/ytortorella/python36/bin/python3
# Copyright (C) 2022-2023 ETH Zurich and University of Bologna
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Yvan Tortorella (yvan.tortorella@unibo.it)
#

import numpy as np
import torch 
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import argparse
import dump_utils as dump
import os

# COMPUTE:
# Z[m_size, k_size] = ( X[m_size, n_size] max W[n_size, k_size] ) + Y[m_size, k_size]

#Visualize data with more precision
torch.set_printoptions(precision=10, sci_mode=False)

parser = argparse.ArgumentParser("mm Operation Test")
parser.add_argument( '--m_size', type=int, default=3 )
parser.add_argument( '--n_size', type=int, default=3 )
parser.add_argument( '--k_size', type=int, default=3 )
parser.add_argument( '--file_name', type=str, default='net_parameters.h')
parser.add_argument( '--inc_dir', type=str)
parser.add_argument( '--txt_dir', type=str)
args = parser.parse_args()

# Network parameters
m_size = args.m_size
n_size = args.n_size
k_size = args.k_size

f = open(args.file_name, "w")

# We want to perform a GEMM, of the kind Z = Y + X*W
# Test Matrices
X = torch.rand(m_size, n_size).half()
W = torch.rand(n_size, k_size).half()
Y = torch.rand(m_size, k_size).half()
Z = torch.rand(m_size, k_size).half()

print("\nInput Data: ")
print("\nX is: ", X, X.shape, X.dtype)
f.write('fp16 X[IN_CH*MID_CH] = {'+dump.tensor_to_string(X)+'};\n')

print("\nW is: ", W, W.shape, W.dtype)
f.write('fp16 W[MID_CH*OUT_CH] = {'+dump.tensor_to_string(W)+'};\n')

print("\nY is: ", Y, Y.shape, Y.dtype)
f.write('fp16 Y[MID_CH*OUT_CH] = {'+dump.tensor_to_string(Y)+'};\n')

print("\nComputing matrix multiplication..")
Z = torch.add(input = Y, other = torch.mm(input = X, mat2 = W))

print("\nZ is: ", Z, Z.shape, Z.dtype)
f.write('fp16 Z[IN_CH*OUT_CH] = {'+dump.tensor_to_string(Z)+'};\n')

print("\n\n")

f.close()

# Matrices conversion to hexadecimal and txt files generation
txt_path = args.txt_dir
for f in os.listdir(txt_path):
    os.remove(os.path.join(txt_path, f))
# os.mkdir(txt_path)
f_x = open(''+txt_path+'/x_input.txt', "w")
for i in range(m_size):
    for j in range (n_size):
        x_bin = bin(np.float16(X[i][j]).view('H'))[2:].zfill(16)
        x_hex = hex(int(x_bin, 2))[2:]
        f_x.write(x_hex)
        f_x.write(' ')
    f_x.write("\n")
f_x.close()

f_w = open(''+txt_path+'/w_input.txt', "w")
for i in range(n_size):
    for j in range (k_size):
        w_bin = bin(np.float16(W[i][j]).view('H'))[2:].zfill(16)
        w_hex = hex(int(w_bin, 2))[2:]
        f_w.write(w_hex)
        f_w.write(' ')
    f_w.write("\n")
f_w.close()

f_y = open(''+txt_path+'/y_input.txt', "w")
for i in range(m_size):
    for j in range (k_size):
        y_bin = bin(np.float16(Y[i][j]).view('H'))[2:].zfill(16)
        y_hex = hex(int(y_bin, 2))[2:]
        f_y.write(y_hex)
        f_y.write(' ')
    f_y.write("\n")
f_y.close()

f_z = open(''+txt_path+'/z_output.txt', "w")
for i in range(m_size):
    for j in range (k_size):
        z_bin = bin(np.float16(Z[i][j]).view('H'))[2:].zfill(16)
        z_hex = hex(int(z_bin, 2))[2:]
        f_z.write(z_hex)
        f_z.write(' ')
    f_z.write("\n")
f_z.close()

in_rows  = str(m_size)
in_cols  = str(n_size)
out_cols = str(k_size)
x_dim    = str(m_size*n_size)
w_dim    = str(n_size*k_size)
y_dim    = str(m_size*k_size)
z_dim    = str(m_size*k_size)
out_int  = str(int(m_size*k_size/2))

# ------------------------------------------------------------------------------------#
#                             Header files generation                                 #
# ------------------------------------------------------------------------------------#

# Path to the genereted files
inc_path = args.inc_dir
for f in os.listdir(inc_path):
    os.remove(os.path.join(inc_path, f))

f_x = open(''+inc_path+'/x_input.h', "w")
f_x.write('uint16_t x_inp ['+x_dim+'] = {\n')
for i in range(m_size):
    for j in range (n_size):
        x_bin = bin(np.float16(X[i][j]).view('H'))[2:].zfill(16)
        x_hex = hex(int(x_bin, 2))[2:]
        if (i == m_size - 1 and j == n_size - 1):
          f_x.write('0x'+x_hex+' ')
        else:
          f_x.write('0x'+x_hex+', ')
    f_x.write("\n")
f_x.write("};")
f_x.close()

f_x = open(''+inc_path+'/x_2D.h', "w")
f_x.write('uint16_t x_inp_2D ['+in_rows+']['+in_cols+'] = {\n')
for i in range(m_size):
    for j in range (n_size):
        x_bin = bin(np.float16(X[i][j]).view('H'))[2:].zfill(16)
        x_hex = hex(int(x_bin, 2))[2:]
        if (i == m_size - 1 and j == n_size - 1):
          f_x.write('0x'+x_hex+' ')
        else:
          f_x.write('0x'+x_hex+', ')
    f_x.write("\n")
f_x.write("};")
f_x.close()

f_w = open(''+inc_path+'/w_input.h', "w")
f_w.write('uint16_t w_inp ['+w_dim+'] = {\n')
for i in range(n_size):
    for j in range (k_size):
        w_bin = bin(np.float16(W[i][j]).view('H'))[2:].zfill(16)
        w_hex = hex(int(w_bin, 2))[2:]
        if (i == n_size - 1 and j == k_size - 1):
          f_w.write('0x'+w_hex+' ')
        else:
          f_w.write('0x'+w_hex+', ')
    f_w.write("\n")
f_w.write("};")
f_w.close()

f_w = open(''+inc_path+'/w_2D.h', "w")
f_w.write('uint16_t w_inp_2D ['+in_cols+']['+out_cols+'] = {\n')
for i in range(n_size):
    for j in range (k_size):
        w_bin = bin(np.float16(W[i][j]).view('H'))[2:].zfill(16)
        w_hex = hex(int(w_bin, 2))[2:]
        if (i == n_size - 1 and j == k_size - 1):
          f_w.write('0x'+w_hex+' ')
        else:
          f_w.write('0x'+w_hex+', ')
    f_w.write("\n")
f_w.write("};")
f_w.close()

f_y = open(''+inc_path+'/y_input.h', "w")
f_y.write('uint16_t y_inp ['+y_dim+'] = {\n')
for i in range(m_size):
    for j in range (k_size):
        y_bin = bin(np.float16(Y[i][j]).view('H'))[2:].zfill(16)
        y_hex = hex(int(y_bin, 2))[2:]
        if (i == m_size - 1 and j == k_size - 1):
          f_y.write('0x'+y_hex+' ')
        else:
          f_y.write('0x'+y_hex+', ')
    f_y.write("\n")
f_y.write("};")
f_y.close()

f_y = open(''+inc_path+'/y_2D.h', "w")
f_y.write('uint16_t y_inp_2D ['+in_cols+']['+out_cols+'] = {\n')
for i in range(m_size):
    for j in range (k_size):
        y_bin = bin(np.float16(Y[i][j]).view('H'))[2:].zfill(16)
        y_hex = hex(int(y_bin, 2))[2:]
        if (i == m_size - 1 and j == k_size - 1):
          f_y.write('0x'+y_hex+' ')
        else:
          f_y.write('0x'+y_hex+', ')
    f_y.write("\n")
f_y.write("};")
f_y.close()


f_z = open(''+inc_path+'/z_output.h', "w")
f_z.write('uint16_t z_oup ['+z_dim+'] = {\n')
for i in range(m_size):
    for j in range (k_size):
        z_bin = bin(np.float16(Z[i][j]).view('H'))[2:].zfill(16)
        z_hex = hex(int(z_bin, 2))[2:]
        if (i == m_size - 1 and j == k_size - 1):
          f_z.write('0x'+z_hex+' ')
        else:
          f_z.write('0x'+z_hex+', ')
    f_z.write("\n")
f_z.write("};")
f_z.close()

f_z = open(''+inc_path+'/z_2D.h', "w")
f_z.write('uint16_t z_oup_2D ['+in_rows+']['+out_cols+'] = {\n')
for i in range(m_size):
    for j in range (k_size):
        z_bin = bin(np.float16(Z[i][j]).view('H'))[2:].zfill(16)
        z_hex = hex(int(z_bin, 2))[2:]
        if (i == m_size - 1 and j == k_size - 1):
          f_z.write('0x'+z_hex+' ')
        else:
          f_z.write('0x'+z_hex+', ')
    f_z.write("\n")
f_z.write("};")
f_z.close()

# Writing tensors' dimensions
f_d = open(''+inc_path+'/tensor_dim.h', "w")
f_d.write('#ifndef __TENSOR_DIM__\n'       )
f_d.write('#define __TENSOR_DIM__\n\n'     )
f_d.write('#define M_SIZE  '+in_rows+' \n' )
f_d.write('#define N_SIZE  '+in_cols+' \n' )
f_d.write('#define K_SIZE  '+out_cols+'\n' )
f_d.write('#define SRC_FMT FP16\n'         )
f_d.write('#define DST_FMT FP16\n'         )
f_d.write('#define FPFORMAT 16\n'          )
f_d.write('uint8_t gemm_ops = GEMM; \n'    )
f_d.write('\n#endif\n'                     )
f_d.close()

#------------------------------------------------------------------------------------------#
#                                     32-bits parser                                       #
#------------------------------------------------------------------------------------------#

f_c = open(''+inc_path+'/golden.h', "w")
f_c.write('uint32_t golden ['+out_int+'] = {\n')
for i in range(m_size):
    j = 0
    while j < k_size - 1:
        c_bin_0 = bin(np.float16(Z[i][j]).view('H'))[2:].zfill(16)
        c_bin_1 = bin(np.float16(Z[i][j+1]).view('H'))[2:].zfill(16)
        c_hex_0 = hex(int(c_bin_0, 2))[2:]
        c_hex_1 = hex(int(c_bin_1, 2))[2:]
        c_hex   = c_hex_1+c_hex_0
        f_c.write('0x'+c_hex+',\n')
        j += 2
f_c.write("};")
f_c.close()