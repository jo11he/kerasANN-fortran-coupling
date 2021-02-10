# builder.py
# run through make_test.sh or manually according to README instructions

import sys
import cffi

ffibuilder = cffi.FFI()

if len(sys.argv) < 2: raise ValueError('missing input at position 1 ($OSTYPE)')
else: OS = sys.argv[1]

header = '''
extern void get_rates(double *, double *, double *, double *, double *, int32_t *, double *, double *);
'''

module = '''

import numpy as np

import sys
# add local dir to load own modules 
sys.path.extend(['./pythonANN']) #(gearbox, prediction_pipe)
import gearbox
import prediction_pipe

from my_plugin import ffi

@ffi.def_extern()
def get_rates(x1_ptr, x2_ptr, x3_ptr, x4_ptr, x5_ptr, n_ptr, y1_ptr, y2_ptr):
    
    # gearbox in
    T_gas = gearbox.as_single(ffi, x1_ptr)
    nH = gearbox.as_single(ffi, x2_ptr) 
    n_H = gearbox.as_single(ffi, x3_ptr)
    n = gearbox.as_single(ffi, n_ptr)
    lam = gearbox.as_array(ffi, x4_ptr, shape=(n,))
    u = gearbox.as_array(ffi, x5_ptr, shape=(n,))
    
    # call python main function
    LH, ER = prediction_pipe.make_prediction(T_gas, nH, n_H, lam, u, create_checkpoints=True)
    
    # gearbox out
    gearbox.get(LH, y1_ptr, 1, ffi)
    gearbox.get(ER, y2_ptr, 1, ffi)
    
'''

with open('plugin.h', 'w') as f:
    f.write(header)



if 'linux' in OS:

    print('building dynamic libs for linux')
    ffibuilder.embedding_api(header)
    ffibuilder.set_source('my_plugin', r'''
            #include "plugin.h"
    ''',
                          extra_link_args=["-L/shared/apps/python/3.6.7/lib"]
                          )

    ffibuilder.embedding_init_code(module)
    ffibuilder.compile(target='libplugin.so', verbose=True)


elif 'darwin' in OS:

    print('building dynamic libs for macOS')
    ffibuilder.embedding_api(header)
    ffibuilder.set_source('my_plugin', r'''
            #include "plugin.h"
    ''')

    ffibuilder.embedding_init_code(module)
    ffibuilder.compile(target='libplugin.dylib', verbose=True)


